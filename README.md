# ⚔ SQLgard — O Despertar do Kernel Ancestral

RPG Engine com motor atômico em PL/SQL, interface Python/Flask e deploy no Vercel.

---

## 📁 Estrutura do Projeto

```
sqlgard/
├── api/
│   └── index.py          # Flask app — entry-point para o Vercel
├── templates/
│   └── index.html        # Interface visual do jogo
├── init_db.sql           # Script de criação do banco + bloco PL/SQL
├── requirements.txt      # Dependências Python
├── vercel.json           # Configuração de deploy
└── README.md
```

---

## 🚀 Deploy no Vercel

### 1. Fork / Clone o repositório no GitHub

```bash
git init
git add .
git commit -m "feat: SQLgard RPG Engine"
git remote add origin https://github.com/SEU_USUARIO/sqlgard.git
git push -u origin main
```

### 2. Importe no Vercel

- Acesse [vercel.com](https://vercel.com) → **Add New Project**
- Selecione o repositório `sqlgard`
- Framework Preset: **Other**
- Clique em **Deploy**

### 3. Configure as Variáveis de Ambiente

No painel Vercel → **Settings → Environment Variables**, adicione:

| Variável      | Exemplo de valor               |
|---------------|-------------------------------|
| `DB_USER`     | `system`                      |
| `DB_PASSWORD` | `minha_senha_secreta`         |
| `DB_DSN`      | `oracle-host:1521/XEPDB1`    |

> ⚠️ **Nunca** coloque credenciais no código-fonte!

### 4. Inicialize o Banco Oracle

Execute o arquivo `init_db.sql` no seu Oracle (SQL*Plus, SQL Developer, etc.):

```bash
sqlplus usuario/senha@host:1521/service < init_db.sql
```

---

## 🔧 Desenvolvimento Local

```bash
# Instale as dependências
pip install -r requirements.txt

# Exporte as variáveis de ambiente
export DB_USER="seu_usuario"
export DB_PASSWORD="sua_senha"
export DB_DSN="localhost:1521/XEPDB1"

# Rode a aplicação
python api/index.py
# Acesse: http://localhost:5000
```

---

## 🎮 Como o Jogo Funciona

| Ação              | Rota HTTP       | O que faz                                       |
|-------------------|-----------------|-------------------------------------------------|
| Carregar heróis   | `GET /herois`   | Retorna todos os heróis em JSON                 |
| Processar turno   | `POST /processar` | Executa o bloco PL/SQL — motor atômico         |
| Reiniciar         | `POST /resetar`  | Restaura HP e status de todos os heróis         |

### Bloco PL/SQL (Motor Atômico)

O bloco `DECLARE...BEGIN...END` no banco Oracle:
1. Declara `v_dano_nevoa := 15` e `v_novo_hp`
2. Abre um **Cursor explícito** com `FOR UPDATE` para todos os heróis `ATIVO`
3. **Loop** `FOR r IN c_herois` — itera sobre cada herói
4. Calcula o novo HP e decide: `UPDATE` com novo HP ou com `status = 'CAÍDO'`
5. `COMMIT` atômico ao final

---

## 📋 Requisitos Atendidos

- ✅ **Bloco Anônimo** (`DECLARE...BEGIN...END`)
- ✅ **Variáveis** para dano e HP intermediário
- ✅ **Cursor Explícito** com `FOR UPDATE`
- ✅ **Loop** (`FOR r IN cursor`)
- ✅ **Conectividade** via `python-oracledb`
- ✅ **Segurança** via `os.environ` para credenciais
- ✅ **Rota `/processar`** que dispara o PL/SQL
- ✅ **Interface Visual** com estado dos heróis e botão "Próximo Turno"
- ✅ **Deploy** pronto para Vercel
