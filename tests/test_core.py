import pytest
from src.core.project import Project
from src.core.tables import Table
from src.configs import DATAPATH

def test_project_lifecycle():
    name = "test_lifecycle"
    password = "pass"
    p = Project(name, password)

    p.new_project()
    assert p.path.exists()

    auth_p = Project(name, password).open_project()
    assert auth_p.is_authenticated

    wrong_p = Project(name, "wrong").open_project()
    assert wrong_p is None

    p.delete_project()
    assert not p.path.exists()

def test_project_with_enc_password(temp_project_with_enc):
    p = temp_project_with_enc
    auth = p.open_project()
    assert auth.is_authenticated
    assert auth.enc_password == "enc_password_456"

def test_project_delete_wrong_password(temp_project):
    name = temp_project.name
    wrong = Project(name, "wrong")
    wrong.delete_project()
    assert temp_project.path.exists()

def test_project_delete_nonexistent():
    p = Project("nonexistent_12345", "pass")
    p.delete_project()

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

    record = {"name": "marcos", "secret": "shhh"}
    assert t.insert(record, p.enc_password)

    results = t.select(p.enc_password, where={"name": "marcos"})
    assert len(results) == 1
    assert results[0]["secret"] == "shhh"

    rid = results[0]["_id"]
    assert t.update_record(rid, {"secret": "new_secret"}, p.enc_password)

    updated = t.select(p.enc_password, where={"_id": rid})
    assert updated[0]["secret"] == "new_secret"

    assert t.delete_record(rid)
    assert len(t.select(p.enc_password)) == 0

    t.delete()
    assert not t.path.exists()

def test_table_schema_validation(temp_project):
    p = temp_project.open_project()
    table_name = "test_validation"
    schema = {"age": {"type": "int", "encrypted": False}}
    t = Table(p, table_name)
    t.create(schema)

    assert not t.insert({"age": "not_a_number"}, p.enc_password)
    assert t.insert({"age": 25}, p.enc_password)

    t.delete()

def test_table_bool_vs_int(temp_project):
    p = temp_project.open_project()
    table_name = "test_bool_vs_int"
    schema = {"flag": {"type": "bool", "encrypted": False}, "count": {"type": "int", "encrypted": False}}
    t = Table(p, table_name)
    t.create(schema)

    assert t.insert({"flag": True, "count": 42}, p.enc_password)
    results = t.select(p.enc_password)
    assert results[0]["flag"] is True
    assert results[0]["count"] == 42

    t.delete()
