from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from src.api.api import Mangadb
from src.configs import API_HOST, API_PORT, API_DEBUG, ALLOWED_ORIGINS
import uvicorn

app = FastAPI(
    title="MangaDB Web API",
    description="Interface REST para o MangaDB",
    version="1.0.0",
    debug=API_DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db(project: str, table: str, password: str) -> Mangadb:
    """Inicializa, conecta e seleciona tabela. Levanta HTTPException em caso de falha."""
    db = Mangadb(project, password)
    if not db.connect():
        raise HTTPException(status_code=401, detail="Credenciais invalidas ou projeto nao encontrado")
    try:
        db.select_table(table)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Tabela '{table}' nao encontrada")
    return db


# --- Autenticação ---

@app.post("/projects/{project}/auth")
async def authenticate(project: str, password: str = Body(..., embed=True)):
    """Valida credenciais do projeto"""
    db = Mangadb(project, password)
    if db.connect():
        tables = db.list_tables()
        return {"status": "ok", "project": project, "tables": tables}
    raise HTTPException(status_code=401, detail="Credenciais invalidas")


# --- Tabelas ---

@app.get("/projects/{project}/tables")
async def list_tables(project: str, x_project_password: str = Header(...)):
    """Lista todas as tabelas de um projeto"""
    db = Mangadb(project, x_project_password)
    if not db.connect():
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    return {"tables": db.list_tables()}


# --- CRUD de Registros ---

@app.post("/projects/{project}/tables/{table}/insert")
async def insert_record(
    project: str,
    table: str,
    data: Dict[str, Any],
    x_project_password: str = Header(...)
):
    """Insere um novo registro"""
    db = get_db(project, table, x_project_password)
    try:
        if db.insert(data):
            return {"status": "ok", "message": "Registro inserido"}
        raise HTTPException(status_code=400, detail="Falha na insercao. Verifique os dados contra o schema.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/projects/{project}/tables/{table}/query")
async def query_records(
    project: str,
    table: str,
    where: Optional[Dict[str, Any]] = Body(default=None),
    query: Optional[str] = Body(default=None, description="Query rica: ex 'idade>18 AND nome LIKE Mar'"),
    x_project_password: str = Header(...)
):
    """Busca registros com filtros opcionais.

    Aceita dois modos de filtro (podem ser combinados):
    - where: {"campo": "valor"} — filtro exato legado
    - query: "campo>valor AND campo LIKE texto" — queries ricas
    """
    db = get_db(project, table, x_project_password)
    results = db.query(where=where, query_str=query)
    return {"count": len(results), "results": results}


@app.put("/projects/{project}/tables/{table}/{record_id}")
async def update_record(
    project: str,
    table: str,
    record_id: str,
    updates: Dict[str, Any],
    x_project_password: str = Header(...)
):
    """Atualiza um registro existente"""
    db = get_db(project, table, x_project_password)
    if db.update(record_id, updates):
        return {"status": "ok", "message": "Registro atualizado"}
    raise HTTPException(status_code=404, detail="Registro nao encontrado")


@app.delete("/projects/{project}/tables/{table}/{record_id}")
async def delete_record(
    project: str,
    table: str,
    record_id: str,
    x_project_password: str = Header(...)
):
    """Deleta um registro"""
    db = get_db(project, table, x_project_password)
    if db.delete(record_id):
        return {"status": "ok", "message": "Registro removido"}
    raise HTTPException(status_code=404, detail="Registro nao encontrado")


# --- Health Check ---

@app.get("/health")
async def health():
    """Verifica se a API esta rodando"""
    return {"status": "ok", "service": "MangaDB Web API"}


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
