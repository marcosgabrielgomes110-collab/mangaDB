import pytest
from src.api.api import Mangadb
from src.core.tables import Table

def test_mangadb_local_api(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"data": {"type": "str", "encrypted": False}})

    db = Mangadb(name, password, password, table_name)
    assert db.connect()

    record_id = db.insert({"data": "payload"})
    assert record_id is not None

    res = db.query(where={"data": "payload"})
    assert len(res) == 1
    rid = res[0]["_id"]

    assert db.update(rid, {"data": "new_payload"})

    tables = db.list_tables()
    assert table_name in tables

    assert db.delete(rid)
    assert len(db.query()) == 0

def test_mangadb_wrong_password(temp_project):
    name = temp_project.name
    db = Mangadb(name, "wrong_password")
    assert not db.connect()

def test_mangadb_query_rich(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_rich_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"nome": {"type": "str", "encrypted": False}, "idade": {"type": "int", "encrypted": False}})
    t.insert({"nome": "Alice", "idade": 30}, password)
    t.insert({"nome": "Bob", "idade": 25}, password)

    db = Mangadb(name, password, password, table_name)
    db.connect()

    res = db.query(query_str="idade>25")
    assert len(res) == 1
    assert res[0]["nome"] == "Alice"

def test_mangadb_check_connection_fails(temp_project):
    db = Mangadb("nonexistent", "pass")
    with pytest.raises(ConnectionError):
        db.list_tables()

def test_mangadb_context_manager(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_ctx_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"x": {"type": "str", "encrypted": False}})

    with Mangadb(name, password, password, table_name) as db:
        rid = db.insert({"x": "ctx works"})
        assert rid is not None
        assert db.count() == 1
        found = db.query_one(where={"x": "ctx works"})
        assert found is not None
        assert found["x"] == "ctx works"

def test_mangadb_query_one(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_q1_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"v": {"type": "int", "encrypted": False}})
    t.insert({"v": 1}, password)

    db = Mangadb(name, password, password, table_name)
    db.connect()
    assert db.query_one(where={"v": 1}) is not None
    assert db.query_one(where={"v": 999}) is None

def test_mangadb_count(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_count_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"v": {"type": "int", "encrypted": False}})
    t.insert({"v": 1}, password)
    t.insert({"v": 2}, password)

    db = Mangadb(name, password, password, table_name)
    db.connect()
    assert db.count() == 2
    assert db.count(where={"v": 1}) == 1

def test_mangadb_table_exists(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_exists_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"x": {"type": "str", "encrypted": False}})

    db = Mangadb(name, password, password)
    db.connect()
    assert db.table_exists(table_name) is True
    assert db.table_exists("nao_existe") is False

def test_mangadb_lazy_connect(temp_project):
    name = temp_project.name
    password = temp_project.password
    table_name = "api_lazy_table"

    p_auth = temp_project.open_project()
    t = Table(p_auth, table_name)
    t.create({"x": {"type": "str", "encrypted": False}})

    db = Mangadb(name, password, password, table_name)
    assert not db.connected
    rid = db.insert({"x": "lazy"})
    assert rid is not None
    assert db.connected
