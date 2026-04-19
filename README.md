<p align="center">
  <h1 align="center">🗄️ MangaDB</h1>
  <p align="center">
    Banco de dados local orientado a projetos, com criptografia AES-256, shell interativo e API REST.
    <br />
    <em>Leve, sem servidor externo, tudo em JSON + TOML.</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
  <img src="https://img.shields.io/badge/storage-JSON%20%2B%20TOML-orange" />
  <img src="https://img.shields.io/badge/encryption-AES--256--GCM-blueviolet" />
</p>

---

## ✨ Features

| Recurso | Descrição |
|---|---|
| **Projetos isolados** | Cada projeto é uma pasta independente com suas próprias tabelas |
| **Autenticação por senha** | SHA-256 hash — projetos protegidos contra acesso não autorizado |
| **Criptografia AES-256-GCM** | Campos marcados como `encrypted` são cifrados no disco com uma senha separada |
| **Schema tipado** | Cada tabela define tipos (`str`, `int`, `float`, `bool`) e valida na inserção |
| **Queries ricas** | `=` `!=` `>` `<` `>=` `<=` `LIKE` `STARTS` `ENDS` `IN` `BETWEEN` com `AND` |
| **Shell interativo** | CLI colorido com comandos curtos para CRUD completo |
| **API REST (FastAPI)** | Servidor embutido com Swagger UI para integrações externas |
| **API programática** | Classe `Mangadb` para usar diretamente em scripts Python |
| **File locking** | Proteção contra corrupção por acesso simultâneo (`filelock`) |
| **Testes automatizados** | Suite com Pytest cobrindo core, queries e endpoints |

---

## 📁 Estrutura do Projeto

```
mangaDB/
├── main.py              # Ponto de entrada (shell)
├── requirements.txt
├── pytest.ini
├── DATA/                # Dados persistidos (criado automaticamente)
│   ├── CONFIG.toml      # Registro de projetos
│   └── meu_projeto/     # Pasta de um projeto
│       └── tabela.json  # Arquivo de uma tabela
├── src/
│   ├── configs.py       # Caminhos, configurações globais e persistência TOML
│   ├── api/
│   │   ├── api.py       # Classe Mangadb (API programática)
│   │   └── app.py       # Servidor FastAPI (REST)
│   ├── cli/
│   │   ├── shell.py     # Loop principal do shell
│   │   └── handlers.py  # Handlers de comando (Project, Table, Record, System)
│   └── core/
│       ├── project.py   # Gerenciamento de projetos
│       ├── tables.py    # CRUD de tabelas com criptografia
│       ├── query.py     # Motor de queries avançado
│       └── utils.py     # Validação e logging colorido
└── tests/
    ├── conftest.py
    ├── test_core.py
    ├── test_api.py
    ├── test_query.py
    └── test_web.py
```

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/marcosgabrielgomes110-collab/mangaDB.git
cd mangaDB

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## 🖥️ Uso — Shell Interativo

```bash
python main.py
```

O shell exibirá o prompt `MangaDB>`. Ao abrir um projeto, o prompt muda para `MangaDB [meu_projeto]>`.

### Comandos disponíveis

#### Projetos

| Comando | Ação |
|---|---|
| `newp` | Criar novo projeto (pede nome, senha de autenticação e senha de criptografia) |
| `openp` | Abrir projeto existente |
| `listp` | Listar todos os projetos |
| `delp` | Deletar projeto (requer senha) |

#### Tabelas (requer projeto aberto)

| Comando | Ação |
|---|---|
| `newt` | Criar tabela com schema interativo |
| `listt` | Listar tabelas do projeto |
| `showt` | Visualizar schema e dados brutos |
| `delt` | Deletar tabela |

#### Registros (requer projeto aberto)

| Comando | Ação |
|---|---|
| `insert` | Inserir registro (valida tipos do schema) |
| `query` | Buscar registros com filtros avançados |
| `update` | Atualizar campos de um registro por ID |
| `delr` | Deletar registro por ID |

#### Sistema

| Comando | Ação |
|---|---|
| `stats` | Estatísticas do banco e projeto |
| `server start` | Iniciar API REST em background |
| `server stop` | Parar a API |
| `server status` | Ver status e endpoints |
| `test` | Rodar suíte de testes |
| `clearcache` | Limpar cache do sistema |
| `home` | Fechar projeto atual |
| `clear` | Limpar terminal |
| `exit` | Sair do MangaDB |

### Exemplo completo no shell

```
MangaDB> newp
Nome: biblioteca
Senha de autenticacao: minhasenha
Senha de criptografia (ENTER para usar a mesma):
✔ Projeto 'biblioteca' criado com sucesso.

MangaDB> openp
Nome: biblioteca
Senha de autenticacao: minhasenha
Senha de criptografia (ENTER para usar a mesma):
✔ Projeto 'biblioteca' aberto.

MangaDB [biblioteca]> newt
Nome da tabela: mangas
Colunas (enter vazio para finalizar):
  coluna: titulo
  tipo de 'titulo': str
  criptografar 'titulo'? (y/n): n
  coluna: autor
  tipo de 'autor': str
  criptografar 'autor'? (y/n): n
  coluna: nota
  tipo de 'nota': int
  criptografar 'nota'? (y/n): n
  coluna:
✔ Tabela 'mangas' criada com sucesso.

MangaDB [biblioteca]> insert
Tabela: mangas
  titulo (str): One Piece
  autor (str): Eiichiro Oda
  nota (int): 10
✔ Registro inserido com sucesso.

MangaDB [biblioteca]> query
Tabela: mangas
  Operadores: = != > < >= <= LIKE STARTS ENDS IN BETWEEN
  Combinação: use AND ou vírgula  (ex: idade>18 AND nome LIKE Mar)
Filtro (vazio para todos): nota>=8 AND autor LIKE Oda
ℹ 1 registro(s) encontrado(s):
  [a1b2c3d4] {'titulo': 'One Piece', 'autor': 'Eiichiro Oda', 'nota': 10}
```

---

## 🔍 Motor de Queries

O MangaDB suporta queries ricas para buscar registros. Use os operadores abaixo:

| Operador | Exemplo | Descrição |
|---|---|---|
| `=` | `nome=Marcos` | Igualdade (case-insensitive) |
| `!=` | `status!=ativo` | Diferença |
| `>` | `idade>18` | Maior que |
| `<` | `preco<100` | Menor que |
| `>=` | `nota>=7` | Maior ou igual |
| `<=` | `nota<=10` | Menor ou igual |
| `LIKE` | `nome LIKE Mar` | Contém substring (case-insensitive) |
| `STARTS` | `nome STARTS On` | Começa com |
| `ENDS` | `email ENDS .com` | Termina com |
| `IN` | `status IN ativo,pendente` | Valor está na lista |
| `BETWEEN` | `idade BETWEEN 18,65` | Dentro do intervalo |

**Combinar condições** com `AND` ou `,`:

```
nota>=8 AND autor LIKE Oda
idade>18, nome STARTS Mar
```

---

## 🔐 Criptografia

O MangaDB usa **AES-256-GCM** para criptografar campos sensíveis no disco.

- Ao criar um projeto, você define uma **senha de autenticação** (para abrir/deletar o projeto) e uma **senha de criptografia** (para cifrar/decifrar campos). Se omitir a segunda, ela usa a mesma da autenticação.
- Ao criar uma tabela, cada coluna pode ser marcada como `encrypted: true`.
- Os dados criptografados ficam armazenados como Base64 no JSON. Ao fazer `query` ou `select`, são descriptografados automaticamente em memória.

---

## 🌐 API REST

O MangaDB embute um servidor FastAPI para integrações externas.

### Iniciar/parar via shell

```
MangaDB> server start
✔ Servidor iniciado com sucesso! (PID: 12345)
ℹ Acesse: http://0.0.0.0:8000/docs para documentação.

MangaDB> server stop
✔ Servidor (PID: 12345) parado com sucesso.
```

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/projects/{project}/auth` | Autenticar no projeto |
| `GET` | `/projects/{project}/tables` | Listar tabelas |
| `POST` | `/projects/{project}/tables/{table}/insert` | Inserir registro |
| `POST` | `/projects/{project}/tables/{table}/query` | Buscar registros |
| `PUT` | `/projects/{project}/tables/{table}/{id}` | Atualizar registro |
| `DELETE` | `/projects/{project}/tables/{table}/{id}` | Deletar registro |
| `GET` | `/health` | Health check |

A senha do projeto é enviada via header `X-Project-Password`.

### Exemplo com curl

```bash
# Autenticar
curl -X POST http://localhost:8000/projects/biblioteca/auth \
  -H "Content-Type: application/json" \
  -d '{"password": "minhasenha"}'

# Inserir registro
curl -X POST http://localhost:8000/projects/biblioteca/tables/mangas/insert \
  -H "X-Project-Password: minhasenha" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Naruto", "autor": "Masashi Kishimoto", "nota": 9}'

# Query rica
curl -X POST http://localhost:8000/projects/biblioteca/tables/mangas/query \
  -H "X-Project-Password: minhasenha" \
  -H "Content-Type: application/json" \
  -d '{"query": "nota>=8 AND autor LIKE Kishi"}'
```

### Documentação interativa

Com o servidor rodando, acesse `http://localhost:8000/docs` para a interface Swagger gerada automaticamente.

---

## 🐍 API Programática

Use a classe `Mangadb` diretamente em qualquer script Python:

```python
from src.api import Mangadb

# Conectar
db = Mangadb("biblioteca", "minhasenha", table_name="mangas")
db.connect()

# Inserir
db.insert({"titulo": "Bleach", "autor": "Tite Kubo", "nota": 8})

# Query rica
results = db.query(query_str="nota>=8 AND autor LIKE Kubo")
print(results)

# Query exata (legado)
results = db.query(where={"titulo": "Bleach"})

# Atualizar
db.update(results[0]["_id"], {"nota": 9})

# Deletar
db.delete(results[0]["_id"])

# Listar tabelas
print(db.list_tables())
```

---

## 🧪 Testes

```bash
# Ativar o ambiente virtual
source .venv/bin/activate

# Rodar todos os testes
pytest -v

# Ou de dentro do shell
MangaDB> test
```

---

## ⚙️ Configuração

Variáveis de ambiente opcionais para o servidor:

| Variável | Default | Descrição |
|---|---|---|
| `MANGADB_HOST` | `0.0.0.0` | Host do servidor |
| `MANGADB_PORT` | `8000` | Porta do servidor |
| `MANGADB_DEBUG` | `True` | Modo debug |

---

## 📋 Requisitos

- Python 3.10+
- Dependências: `fastapi`, `uvicorn`, `cryptography`, `tomli-w`, `filelock`
- Testes: `pytest`, `httpx`

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais informações.

---

<p align="center">
  Feito por <a href="https://github.com/marcosgabrielgomes110-collab">Marcos Gabriel Gomes</a>
</p>
