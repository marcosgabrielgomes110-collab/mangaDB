from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from src.api.api import Mangadb
from src.configs import API_HOST, API_PORT, API_DEBUG, ALLOWED_ORIGINS, get_config
from src.core.project import Project
from src.core.tables import Table
import uvicorn

app = FastAPI(
    title="MangaDB Web API",
    description="Interface REST para o MangaDB",
    version="1.1.0",
    debug=API_DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_project(project: str, password: str) -> Project:
    p = Project(project, password)
    result = p.open_project()
    if not result:
        raise HTTPException(status_code=401, detail="Credenciais invalidas ou projeto nao encontrado")
    return result

def get_db(project: str, table: str, password: str) -> Mangadb:
    db = Mangadb(project, password, table_name=table)
    try:
        db.connect()
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciais invalidas ou projeto nao encontrado")
    if not db.table:
        raise HTTPException(status_code=404, detail=f"Tabela '{table}' nao encontrada")
    return db


@app.post("/projects/{project}/auth")
async def authenticate(project: str, password: str = Body(..., embed=True)):
    p = get_project(project, password)
    tables = p.list_tables()
    return {"status": "ok", "project": project, "tables": tables}


@app.get("/projects/{project}/tables")
async def list_tables(project: str, x_project_password: str = Header(...)):
    p = get_project(project, x_project_password)
    return {"tables": p.list_tables()}


@app.post("/projects/{project}/tables/{table}/create")
async def create_table(
    project: str,
    table: str,
    schema: Dict[str, Any],
    x_project_password: str = Header(...)
):
    p = get_project(project, x_project_password)
    t = Table(p, table)
    t.create(schema)
    return {"status": "ok", "message": f"Tabela '{table}' criada"}


@app.delete("/projects/{project}/tables/{table}")
async def delete_table(
    project: str,
    table: str,
    x_project_password: str = Header(...)
):
    p = get_project(project, x_project_password)
    t = Table(p, table)
    t.delete()
    return {"status": "ok", "message": f"Tabela '{table}' removida"}


@app.get("/projects/{project}/tables/{table}/schema")
async def get_schema(
    project: str,
    table: str,
    x_project_password: str = Header(...)
):
    p = get_project(project, x_project_password)
    t = Table(p, table)
    try:
        content = t.show()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Tabela '{table}' nao encontrada")
    return {"schema": content["schema"], "record_count": len(content.get("data", []))}


@app.post("/projects/{project}/tables/{table}/insert")
async def insert_record(
    project: str,
    table: str,
    data: Dict[str, Any],
    x_project_password: str = Header(...)
):
    db = get_db(project, table, x_project_password)
    try:
        record_id = db.insert(data)
        if record_id:
            return {"status": "ok", "id": record_id, "message": "Registro inserido"}
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
    db = get_db(project, table, x_project_password)
    if db.delete(record_id):
        return {"status": "ok", "message": "Registro removido"}
    raise HTTPException(status_code=404, detail="Registro nao encontrado")


@app.get("/projects/{project}/stats")
async def project_stats(
    project: str,
    x_project_password: str = Header(...)
):
    p = get_project(project, x_project_password)
    tables = p.list_tables()
    total_records = 0
    for t_name in tables:
        t = Table(p, t_name)
        total_records += len(t.show().get("data", []))
    return {
        "project": project,
        "tables": len(tables),
        "table_names": tables,
        "total_records": total_records,
    }


@app.get("/health")
async def health():
    config = get_config()
    return {
        "status": "ok",
        "service": "MangaDB Web API",
        "projects": len(config["projects"]) if config else 0,
    }


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
