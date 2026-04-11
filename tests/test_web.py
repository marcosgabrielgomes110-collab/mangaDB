import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.core.tables import Table

client = TestClient(app)

def test_web_api_endpoints(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "web_table"
    
    # Setup
    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"msg": {"type": "str", "encrypted": False}})
    
    headers = {"X-Project-Password": password}
    
    # Test Auth
    resp = client.post(f"/projects/{name}/auth", json={"password": password})
    assert resp.status_code == 200
    
    # Test List Tables
    resp = client.get(f"/projects/{name}/tables", headers=headers)
    assert resp.status_code == 200
    assert table_name in resp.json()["tables"]
    
    # Test Insert
    resp = client.post(
        f"/projects/{name}/tables/{table_name}/insert",
        json={"msg": "hello web"},
        headers=headers
    )
    assert resp.status_code == 200
    
    # Test Query
    resp = client.post(
        f"/projects/{name}/tables/{table_name}/query",
        json={"msg": "hello web"},
        headers=headers
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1
    rid = results[0]["_id"]
    
    # Test Update
    resp = client.put(
        f"/projects/{name}/tables/{table_name}/{rid}",
        json={"msg": "updated web"},
        headers=headers
    )
    assert resp.status_code == 200
    
    # Test Delete
    resp = client.delete(
        f"/projects/{name}/tables/{table_name}/{rid}",
        headers=headers
    )
    assert resp.status_code == 200
    
    # Test Health
    resp = client.get("/health")
    assert resp.status_code == 200
