import os
import json
from flask import Flask, jsonify, render_template_string
import oracledb

app = Flask(__name__)

# ─────────────────────────────────────────────
# Credenciais via variáveis de ambiente (Vercel)
# ─────────────────────────────────────────────
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DSN      = os.environ.get("DB_DSN")   # Ex: host:1521/XEPDB1


def get_connection():
    """Retorna uma conexão com o banco Oracle."""
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )


# ─────────────────────────────────────────────
# BLOCO PL/SQL  – Motor Atômico do Mundo
# ─────────────────────────────────────────────
PLSQL_PROXIMO_TURNO = """
DECLARE
    -- Variável que define o dano da névoa por turno
    v_dano_nevoa   NUMBER := 15;

    -- Variável auxiliar para cálculo de HP resultante
    v_novo_hp      NUMBER;

    -- Cursor explícito: seleciona todos os heróis ainda ativos
    CURSOR c_herois IS
        SELECT id_heroi, nome, hp_atual
          FROM TB_HEROIS
         WHERE status = 'ATIVO'
           FOR UPDATE;          -- bloqueia as linhas para atualização segura

BEGIN
    -- Loop sobre cada herói ativo
    FOR r IN c_herois LOOP

        -- Calcula o HP resultante após o dano da névoa
        v_novo_hp := r.hp_atual - v_dano_nevoa;

        IF v_novo_hp <= 0 THEN
            -- Herói sucumbe à névoa
            UPDATE TB_HEROIS
               SET hp_atual = 0,
                   status   = 'CAÍDO'
             WHERE id_heroi = r.id_heroi;
        ELSE
            -- Herói sobrevive, apenas perde HP
            UPDATE TB_HEROIS
               SET hp_atual = v_novo_hp
             WHERE id_heroi = r.id_heroi;
        END IF;

    END LOOP;

    COMMIT;
END;
"""


# ─────────────────────────────────────────────
# Rotas Flask
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Página principal – retorna o HTML da interface."""
    with open(os.path.join(os.path.dirname(__file__), "../templates/index.html"), "r", encoding="utf-8") as f:
        html = f.read()
    return html


@app.route("/herois", methods=["GET"])
def listar_herois():
    """Retorna a lista de heróis em JSON."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi"
        )
        cols = [d[0].lower() for d in cursor.description]
        herois = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({"success": True, "herois": herois})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/processar", methods=["POST"])
def processar_turno():
    """
    Executa o bloco PL/SQL que processa um turno da névoa.
    Este é o 'motor atômico' do jogo – toda a física roda no banco.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ── Executa o bloco anônimo PL/SQL ──
        cursor.execute(PLSQL_PROXIMO_TURNO)

        # Busca estado atualizado para retornar ao frontend
        cursor.execute(
            "SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi"
        )
        cols = [d[0].lower() for d in cursor.description]
        herois = [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        ativos  = sum(1 for h in herois if h["status"] == "ATIVO")
        caidos  = sum(1 for h in herois if h["status"] == "CAÍDO")

        return jsonify({
            "success": True,
            "herois": herois,
            "resumo": {
                "ativos": ativos,
                "caidos": caidos,
                "nevoa_dano": 15
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/resetar", methods=["POST"])
def resetar_jogo():
    """Restaura todos os heróis ao estado inicial."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE TB_HEROIS
               SET hp_atual = hp_max,
                   status   = 'ATIVO'
        """)
        conn.commit()
        cursor.execute(
            "SELECT id_heroi, nome, classe, hp_atual, hp_max, status FROM TB_HEROIS ORDER BY id_heroi"
        )
        cols = [d[0].lower() for d in cursor.description]
        herois = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({"success": True, "herois": herois})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Necessário para Vercel (WSGI entry-point)
# O Vercel detecta automaticamente `app` como handler Flask
if __name__ == "__main__":
    app.run(debug=True, port=5000)
