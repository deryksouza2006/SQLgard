# ⚔️ SQLgard — O Despertar do Kernel Ancestral

> RPG Engine com motor de jogo atômico em PL/SQL, backend Python/Flask e deploy no Vercel.

---

## 📖 Sobre o Projeto

Um antigo servidor de RPG foi encontrado nos escombros de uma universidade esquecida. O mundo de **SQLgard** está em perigo: uma névoa venenosa está drenando a vida de todos os heróis simultaneamente.

A interface visual exibe o estado dos heróis em tempo real, mas toda a "física" do mundo — o cálculo de danos, a detecção de mortes e a persistência do estado — é processada por um **motor atômico dentro do banco de dados Oracle**, via bloco anônimo PL/SQL.

---

## 🗂️ Estrutura de Pastas

```
SQLgard/
├── api/
│   ├── index.py           # Backend Flask: rotas HTTP + bloco PL/SQL
│   └── templates/
│       └── index.html     # Interface visual dark fantasy do jogo
├── init_db.sql            # Script de criação da tabela e inserção dos heróis
├── requirements.txt       # Dependências Python
├── vercel.json            # Configuração de deploy serverless
└── README.md
```

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Interface | HTML5 + CSS3 + JavaScript puro |
| Backend | Python 3 + Flask |
| Banco de dados | Oracle Database |
| Conector Oracle | `python-oracledb` |
| Deploy | Vercel (serverless) |
| Motor do jogo | PL/SQL (Bloco Anônimo + Cursor + Loop) |

---

## 🧪 Inicialização do Banco de Dados

Execute o arquivo `init_db.sql` no seu cliente Oracle (SQL Developer, SQL*Plus, etc.):

```sql
-- Cria a tabela de heróis
CREATE TABLE TB_HEROIS (
    id_heroi NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome     VARCHAR2(50),
    classe   VARCHAR2(20),
    hp_atual NUMBER,
    hp_max   NUMBER,
    status   VARCHAR2(20) DEFAULT 'ATIVO'
);

-- Insere os heróis iniciais
INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max) VALUES ('Artorias', 'GUERREIRO', 100, 100);
INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max) VALUES ('Sif', 'LADRÃO', 80, 80);
INSERT INTO TB_HEROIS (nome, classe, hp_atual, hp_max) VALUES ('Gwyn', 'MAGO', 60, 60);
COMMIT;
```

---

## ⚡ Motor Atômico — Bloco PL/SQL

Este é o coração do projeto. A cada turno, a rota `/processar` dispara o seguinte bloco anônimo diretamente no banco Oracle:

```sql
DECLARE
    -- Variável com o dano fixo da névoa por turno
    v_dano_nevoa   NUMBER := 15;

    -- Variável auxiliar para o HP resultante
    v_novo_hp      NUMBER;

    -- Cursor explícito: seleciona todos os heróis ativos com bloqueio de linha
    CURSOR c_herois IS
        SELECT id_heroi, nome, hp_atual
          FROM TB_HEROIS
         WHERE status = 'ATIVO'
           FOR UPDATE;

BEGIN
    -- Loop sobre cada herói ativo
    FOR r IN c_herois LOOP

        v_novo_hp := r.hp_atual - v_dano_nevoa;

        IF v_novo_hp <= 0 THEN
            -- Herói sucumbe à névoa
            UPDATE TB_HEROIS
               SET hp_atual = 0, status = 'CAÍDO'
             WHERE id_heroi = r.id_heroi;
        ELSE
            -- Herói sobrevive, perde HP
            UPDATE TB_HEROIS
               SET hp_atual = v_novo_hp
             WHERE id_heroi = r.id_heroi;
        END IF;

    END LOOP;

    COMMIT;
END;
```

### Requisitos PL/SQL atendidos

- ✅ **Bloco Anônimo** — `DECLARE ... BEGIN ... END`
- ✅ **Variáveis** — `v_dano_nevoa` e `v_novo_hp` para cálculos intermediários
- ✅ **Cursor Explícito** — `CURSOR c_herois IS SELECT ... FOR UPDATE`
- ✅ **Estrutura de Repetição** — `FOR r IN c_herois LOOP`
- ✅ **Lógica condicional** — `IF / ELSE` para determinar morte ou dano
- ✅ **Commit atômico** — `COMMIT` ao final do bloco

---

## 🌐 Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Serve a interface visual do jogo |
| `GET` | `/herois` | Retorna todos os heróis em JSON |
| `POST` | `/processar` | Executa o bloco PL/SQL (próximo turno) |
| `POST` | `/resetar` | Restaura todos os heróis ao estado inicial |

---

## 🔐 Segurança — Variáveis de Ambiente

As credenciais do banco **nunca aparecem no código-fonte**. São lidas exclusivamente via `os.environ`:

```python
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DSN      = os.environ.get("DB_DSN")  # Ex: host:1521/XEPDB1
```

---

## 🚀 Deploy no Vercel

### 1. Suba o projeto para o GitHub

```bash
git init
git add .
git commit -m "feat: SQLgard RPG Engine"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/sqlgard.git
git push -u origin main
```

### 2. Importe no Vercel

- Acesse [vercel.com](https://vercel.com) → **Add New Project**
- Selecione o repositório → Framework Preset: **Other**
- Configure as variáveis de ambiente antes de fazer deploy

### 3. Variáveis de Ambiente (Settings → Environment Variables)

| Variável | Exemplo |
|---|---|
| `DB_USER` | `ADMIN` |
| `DB_PASSWORD` | `sua_senha` |
| `DB_DSN` | `host:1521/XEPDB1` |

### 4. Deploy

Clique em **Deploy**. O Vercel instala as dependências do `requirements.txt` e disponibiliza a URL pública automaticamente.

---

## 💻 Rodando Localmente

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
export DB_USER="seu_usuario"
export DB_PASSWORD="sua_senha"
export DB_DSN="localhost:1521/XEPDB1"

# Rode o servidor
python api/index.py

# Acesse em: http://localhost:5000
```

---

## 🎮 Como Jogar

1. Acesse a URL do projeto no Vercel
2. Os 3 heróis aparecem com HP cheio
3. Clique em **⚡ Próximo Turno** — o PL/SQL executa e cada herói perde 15 HP
4. Acompanhe o log de combate para ver quem está sofrendo dano
5. Quando o HP de um herói chega a zero, seu status muda para **CAÍDO**
6. Quando todos caem, o banner **"☠ Todos Caíram ☠"** é exibido
7. Clique em **↺ Reiniciar SQLgard** para restaurar todos os heróis

### Sequência de quedas (dano fixo de 15 HP/turno)

| Turno | Artorias (100 HP) | Sif (80 HP) | Gwyn (60 HP) |
|---|---|---|---|
| 1 | 85 HP | 65 HP | 45 HP |
| 2 | 70 HP | 50 HP | 30 HP |
| 3 | 55 HP | 35 HP | 15 HP |
| 4 | 40 HP | 20 HP | **CAÍDO** |
| 5 | 25 HP | 5 HP | — |
| 6 | 10 HP | **CAÍDO** | — |
| 7 | **CAÍDO** | — | — |

---

## 👤 Autor

Desenvolvido como projeto acadêmico de Banco de Dados — demonstração de integração entre frontend web, backend Python e lógica de negócio em PL/SQL dentro do Oracle Database.
