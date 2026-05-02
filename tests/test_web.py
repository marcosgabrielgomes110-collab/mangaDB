import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.core.tables import Table

client = TestClient(app)

def test_web_api_endpoints(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"msg": {"type": "str", "encrypted": False}})

    headers = {"X-Project-Password": password}

    resp = client.post(f"/projects/{name}/auth", json={"password": password})
    assert resp.status_code == 200

    resp = client.get(f"/projects/{name}/tables", headers=headers)
    assert resp.status_code == 200
    assert table_name in resp.json()["tables"]

    resp = client.post(
        f"/projects/{name}/tables/{table_name}/insert",
        json={"msg": "hello web"},
        headers=headers
    )
    assert resp.status_code == 200

    resp = client.post(
        f"/projects/{name}/tables/{table_name}/query",
        json={"where": {"msg": "hello web"}},
        headers=headers
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    rid = results[0]["_id"]

    resp = client.put(
        f"/projects/{name}/tables/{table_name}/{rid}",
        json={"msg": "updated web"},
        headers=headers
    )
    assert resp.status_code == 200

    resp = client.delete(
        f"/projects/{name}/tables/{table_name}/{rid}",
        headers=headers
    )
    assert resp.status_code == 200

    resp = client.get("/health")
    assert resp.status_code == 200

def test_web_api_auth_fail(temp_project):
    name = temp_project.name
    resp = client.post(f"/projects/{name}/auth", json={"password": "wrong_password"})
    assert resp.status_code == 401

def test_web_api_query_rich(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_query_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"nome": {"type": "str", "encrypted": False}, "idade": {"type": "int", "encrypted": False}})
    t.insert({"nome": "Alice", "idade": 30}, password)
    t.insert({"nome": "Bob", "idade": 25}, password)

    headers = {"X-Project-Password": password}

    resp = client.post(
        f"/projects/{name}/tables/{table_name}/query",
        json={"query": "idade>25"},
        headers=headers
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["nome"] == "Alice"

def test_web_schema_endpoint(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_schema_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"nome": {"type": "str", "encrypted": False}})

    headers = {"X-Project-Password": password}
    resp = client.get(f"/projects/{name}/tables/{table_name}/schema", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "schema" in data
    assert "nome" in data["schema"]

def test_web_stats_endpoint(temp_project):
    name = temp_project.name
    password = temp_project.password

    headers = {"X-Project-Password": password}
    resp = client.get(f"/projects/{name}/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project"] == name
    assert "tables" in data

def test_web_create_table(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_new_table"

    headers = {"X-Project-Password": password}
    schema = {"x": {"type": "str", "encrypted": False}}
    resp = client.post(
        f"/projects/{name}/tables/{table_name}/create",
        json=schema,
        headers=headers
    )
    assert resp.status_code == 200

    p_auth = temp_project.open_project()
    assert (p_auth.path / f"{table_name}.json").exists()

def test_web_insert_returns_id(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_id_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"x": {"type": "str", "encrypted": False}})

    headers = {"X-Project-Password": password}
    resp = client.post(
        f"/projects/{name}/tables/{table_name}/insert",
        json={"x": "test"},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert len(data["id"]) > 0
