import pytest
from src.api.api import Mangadb
from src.core.tables import Table

def test_mangadb_local_api(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_table"
    
    # Setup table manually for API test
    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"data": {"type": "str", "encrypted": False}})
    
    # Use API
    db = Mangadb(name, password, table_name)
    assert db.connect()
    
    # Insert
    assert db.insert({"data": "payload"})
    
    # Query
    res = db.query(where={"data": "payload"})
    assert len(res) == 1
    rid = res[0]["_id"]
    
    # Update
    assert db.update(rid, {"data": "new_payload"})
    
    # List Tables
    tables = db.list_tables()
    assert table_name in tables
    
    # Delete
    assert db.delete(rid)
    assert len(db.query()) == 0
