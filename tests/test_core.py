import pytest
from src.core.project import Project
from src.core.tables import Table
from src.configs import DATAPATH

def test_project_lifecycle():
    name = "test_lifecycle"
    password = "pass"
    p = Project(name, password)
    
    # Create
    p.new_project()
    assert p.path.exists()
    
    # Auth
    auth_p = Project(name, password).open_project()
    assert auth_p.is_authenticated
    
    # Wrong Auth
    wrong_p = Project(name, "wrong").open_project()
    assert wrong_p is None
    
    # Delete
    p.delete_project()
    assert not p.path.exists()

def test_table_crud(temp_project):
    p = temp_project.open_project()
    table_name = "pytest_table"
    schema = {
        "name": {"type": "str", "encrypted": False},
        "secret": {"type": "str", "encrypted": True}
    }
    
    t = Table(p, table_name)
    t.create(schema)
    assert t.path.exists()
    
    # Insert
    record = {"name": "marcos", "secret": "shhh"}
    assert t.insert(record, p.password)
    
    # Select & Decrypt
    results = t.select(p.password, where={"name": "marcos"})
    assert len(results) == 1
    assert results[0]["secret"] == "shhh"
    
    # Update
    rid = results[0]["_id"]
    assert t.update_record(rid, {"secret": "new_secret"}, p.password)
    
    updated = t.select(p.password, where={"_id": rid})
    assert updated[0]["secret"] == "new_secret"
    
    # Delete Record
    assert t.delete_record(rid)
    assert len(t.select(p.password)) == 0
    
    # Delete Table
    t.delete()
    assert not t.path.exists()
