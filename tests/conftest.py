import pytest
import shutil
from pathlib import Path
from src.core.project import Project
from src.configs import DATAPATH

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    yield
    for p in DATAPATH.glob("test_*"):
        if p.is_dir():
            shutil.rmtree(p)

@pytest.fixture
def temp_project():
    name = "test_project_pytest"
    password = "test_password_123"
    p = Project(name, password)

    if p.path.exists():
        p.delete_project()

    p.new_project()
    yield p

    if p.path.exists():
        p.delete_project()

@pytest.fixture
def temp_project_with_enc():
    name = "test_project_enc"
    password = "test_password_123"
    enc_password = "enc_password_456"
    p = Project(name, password, enc_password)

    if p.path.exists():
        p.delete_project()

    p.new_project()
    yield p

    if p.path.exists():
        p.delete_project()

@pytest.fixture
def clean_config():
    from src.configs import CONFIGPATH, _CONFIG_LOCK
    with _CONFIG_LOCK:
        if CONFIGPATH.exists():
            CONFIGPATH.unlink()
    yield
    with _CONFIG_LOCK:
        if CONFIGPATH.exists():
            CONFIGPATH.unlink()
