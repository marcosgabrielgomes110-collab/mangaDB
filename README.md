<p align="center">
  <h1 align="center">MangaDB</h1>
  <p align="center">
    Banco de dados local orientado a projetos, com criptografia AES-256-GCM, TUI interativa e API REST.
    <br />
    <em>Leve, sem servidor externo, tudo em JSON + TOML.</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
  <img src="https://img.shields.io/badge/storage-JSON%20%2B%20TOML-orange" />
  <img src="https://img.shields.io/badge/encryption-AES--256--GCM-blueviolet" />
  <img src="https://img.shields.io/badge/TUI-Rich-gold" />
</p>

---

## Funcionalidades

| Recurso | Descrição |
|---|---|
| **Projetos isolados** | Cada projeto é uma pasta independente com suas próprias tabelas |
| **Autenticação por senha** | PBKDF2-SHA256 com salt — proteção contra brute-force |
| **Criptografia AES-256-GCM** | Campos marcados como `encrypted` são cifrados no disco |
| **Schema tipado** | Cada tabela define tipos (`str`, `int`, `float`, `bool`) e valida na inserção |
| **Queries ricas** | `=` `!=` `>` `<` `>=` `<=` `LIKE` `STARTS` `ENDS` `IN` `BETWEEN` com `AND` |
| **TUI interativa (Rich)** | Terminal com tema amarelo/laranja, tabelas, painéis e prompts estilizados |
| **API REST (FastAPI)** | Servidor embutido com Swagger UI, schema e stats endpoints |
| **API programática** | Classe `Mangadb` com conexão automática, context manager e métodos fluentes |
| **File locking** | Proteção contra corrupção por acesso simultâneo (`filelock`) |
| **Testes automatizados** | 66+ testes com Pytest cobrindo core, queries, API e web |

---

## Estrutura do Projeto

```
mangaDB/
├── main.py                  # Ponto de entrada (TUI)
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── DATA/                    # Dados persistidos (criado automaticamente)
│   ├── CONFIG.toml          # Registro de projetos (PBKDF2 hashes)
│   └── meu_projeto/         # Pasta de um projeto
│       └── tabela.json      # Arquivo de uma tabela (com _key_salt)
├── src/
│   ├── configs.py           # Caminhos, configurações, cache, atomic write
│   ├── api/
│   │   ├── __init__.py      # Exporta Mangadb
│   │   ├── api.py           # Classe Mangadb (API programática)
│   │   └── app.py           # Servidor FastAPI (REST)
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py           # Loop principal da TUI (Rich)
│   │   ├── theme.py         # Cores e estilos (laranja/dourado)
│   │   ├── widgets.py       # Componentes reutilizáveis (tabelas, painéis, inputs)
│   │   └── handlers.py      # Handlers de comando (Project, Table, Record, System)
│   └── core/
│       ├── __init__.py
│       ├── project.py       # Gerenciamento de projetos (PBKDF2)
│       ├── tables.py        # CRUD de tabelas com criptografia + atomic update
│       ├── query.py         # Motor de queries avançado
│       └── utils.py         # Validação e logging colorido
└── tests/
    ├── conftest.py
    ├── test_core.py
    ├── test_api.py
    ├── test_query.py
    ├── test_utils_config.py
    └── test_web.py
```

---

## Docker

```bash
# Construir
docker build -t mangadb .

# Executar TUI (modo interativo)
docker run -it --rm -v mangadb_data:/app/DATA mangadb

# Executar servidor API REST
docker run -d --rm -p 8000:8000 -v mangadb_data:/app/DATA mangadb python -m src.api.app
```

---

## Instalação (local)

```bash
git clone https://github.com/marcosgabrielgomes110-collab/mangaDB.git
cd mangaDB
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Uso — TUI Interativa (Rich)

```bash
python main.py
```

A TUI exibe um banner e o prompt `MangaDB > ` (laranja). Ao abrir um projeto, o prompt muda para `MangaDB [meu_projeto] > ` (laranja + dourado). Tabelas e resultados são renderizados com bordas e cores.

### Comandos

| Comando | Ação |
|---|---|
| `newp` | Criar novo projeto |
| `openp` | Abrir projeto existente |
| `listp` | Listar projetos |
| `delp` | Deletar projeto |
| `newt` | Criar tabela com schema |
| `listt` | Listar tabelas |
| `showt` | Ver schema e dados |
| `delt` | Deletar tabela |
| `insert` | Inserir registro |
| `query` | Buscar com filtros |
| `update` | Atualizar registro por ID |
| `delr` | Deletar registro por ID |
| `stats` | Estatísticas do sistema |
| `server start/stop/status` | Gerenciar API REST |
| `home` | Fechar projeto |
| `test` | Rodar testes |
| `clearcache` | Limpar cache |
| `clear` | Limpar terminal |
| `exit` | Sair |

---

## Motor de Queries

| Operador | Exemplo | Descrição |
|---|---|---|
| `=` | `nome=Marcos` | Igualdade (case-insensitive) |
| `!=` | `status!=ativo` | Diferença |
| `>` | `idade>18` | Maior que |
| `<` | `preco<100` | Menor que |
| `>=` | `nota>=7` | Maior ou igual |
| `<=` | `nota<=10` | Menor ou igual |
| `LIKE` | `nome LIKE Mar` | Contém substring |
| `STARTS` | `nome STARTS On` | Começa com |
| `ENDS` | `email ENDS .com` | Termina com |
| `IN` | `status IN ativo,pendente` | Valor está na lista |
| `BETWEEN` | `idade BETWEEN 18,65` | Dentro do intervalo |

Combine condições com `AND` ou `,`:
```
nota>=8 AND autor LIKE Oda
idade>18, nome STARTS Mar
```

---

## Criptografia

- **Hash de senha**: PBKDF2-SHA256 com salt de 16 bytes (600.000 rounds)
- **Criptografia de campos**: AES-256-GCM com nonce aleatório de 12 bytes
- **Derivação de chave**: PBKDF2-SHA256 com salt próprio armazenado na tabela (`_key_salt`)
- Ao criar um projeto, você define uma senha de autenticação e uma de criptografia (podem ser diferentes)

---

## API REST

### Iniciar

```bash
# Via TUI
MangaDB> server start

# Ou direto
python -m src.api.app
```

### Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/projects/{project}/auth` | Autenticar |
| `GET` | `/projects/{project}/tables` | Listar tabelas |
| `POST` | `/projects/{project}/tables/{table}/create` | Criar tabela com schema |
| `DELETE` | `/projects/{project}/tables/{table}` | Deletar tabela |
| `GET` | `/projects/{project}/tables/{table}/schema` | Schema + contagem |
| `POST` | `/projects/{project}/tables/{table}/insert` | Inserir (retorna `id`) |
| `POST` | `/projects/{project}/tables/{table}/query` | Buscar registros |
| `PUT` | `/projects/{project}/tables/{table}/{id}` | Atualizar registro |
| `DELETE` | `/projects/{project}/tables/{table}/{id}` | Deletar registro |
| `GET` | `/projects/{project}/stats` | Estatísticas do projeto |
| `GET` | `/health` | Health check |

A senha é enviada via header `X-Project-Password`.

### Exemplos com curl

```bash
# Autenticar
curl -X POST http://localhost:8000/projects/biblioteca/auth \
  -H "Content-Type: application/json" \
  -d '{"password": "minhasenha"}'

# Inserir (retorna o id do registro)
curl -X POST http://localhost:8000/projects/biblioteca/tables/mangas/insert \
  -H "X-Project-Password: minhasenha" \
  -H "Content-Type: application/json" \
  -d '{"titulo": "One Piece", "autor": "Oda", "nota": 10}'

# Query rica
curl -X POST http://localhost:8000/projects/biblioteca/tables/mangas/query \
  -H "X-Project-Password: minhasenha" \
  -H "Content-Type: application/json" \
  -d '{"query": "nota>=8 AND autor LIKE Oda"}'

# Ver schema da tabela
curl -X GET http://localhost:8000/projects/biblioteca/tables/mangas/schema \
  -H "X-Project-Password: minhasenha"

# Estatisticas do projeto
curl -X GET http://localhost:8000/projects/biblioteca/stats \
  -H "X-Project-Password: minhasenha"
```

Documentação interativa em `http://localhost:8000/docs`.

---

## API Programática

```python
from src.api import Mangadb

# Conexao automatica (lazy) + context manager
with Mangadb("biblioteca", "minhasenha", table_name="mangas") as db:
    # Insert retorna o ID
    rid = db.insert({"titulo": "Bleach", "autor": "Tite Kubo", "nota": 8})
    print(f"Inserido ID: {rid}")

    # Query rica
    results = db.query(query_str="nota>=8 AND autor LIKE Kubo")

    # Query exata
    results = db.query(where={"titulo": "Bleach"})

    # query_one (retorna None se nao achar)
    found = db.query_one(where={"titulo": "Bleach"})

    # count
    total = db.count()

    # Atualizar
    db.update(results[0]["_id"], {"nota": 9})

    # Deletar
    db.delete(results[0]["_id"])

# Sem context manager (requer connect() manual)
db = Mangadb("biblioteca", "minhasenha", table_name="mangas")
db.connect()
print(db.list_tables())
```

---

## Testes

```bash
source .venv/bin/activate
pytest -v
```

---

## Configuração

| Variável | Default | Descrição |
|---|---|---|
| `MANGADB_HOST` | `0.0.0.0` | Host do servidor |
| `MANGADB_PORT` | `8000` | Porta do servidor |
| `MANGADB_DEBUG` | `False` | Modo debug |
| `MANGADB_ORIGINS` | `http://localhost:8000` | Origens CORS (separadas por vírgula) |

---

## Requisitos

- Python 3.10+
- Dependências: `fastapi`, `uvicorn`, `cryptography`, `rich`, `tomli-w`, `filelock`
- Testes: `pytest`, `httpx`

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).

---

<p align="center">
  Feito por <a href="https://github.com/marcosgabrielgomes110-collab">Marcos Gabriel Gomes</a>
</p>
