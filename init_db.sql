-- ============================================================
--  SQLgard — Script de Inicialização do Banco de Dados
--  Execute este script no Oracle antes de subir a aplicação
-- ============================================================

-- 1. Criar a tabela de heróis
CREATE TABLE TB_HEROIS (
    id_heroi NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome     VARCHAR2(50),
    classe   VARCHAR2(20),
    hp_atual NUMBER,
    hp_max   NUMBER,
    status   VARCHAR2(20) DEFAULT 'ATIVO'
);

-- 2. Inserir os heróis iniciais
INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max)
VALUES ('Artorias', 'GUERREIRO', 100, 100);

INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max)
VALUES ('Sif', 'LADRÃO', 80, 80);

INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max)
VALUES ('Gwyn', 'MAGO', 60, 60);

COMMIT;

-- ============================================================
--  BLOCO PL/SQL — Motor Atômico do Mundo
--  (Este é o bloco executado pela rota /processar da API)
-- ============================================================
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
/
