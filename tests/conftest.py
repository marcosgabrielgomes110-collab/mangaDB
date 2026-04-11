import pytest
import shutil
from pathlib import Path
from src.core.project import Project
from src.configs import DATAPATH

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Garante que dados de teste antigos sejam removidos antes e depois da sessão"""
    yield
    # Limpa opcionalmente pastas que começam com 'test_'
    for p in DATAPATH.glob("test_*"):
        if p.is_dir():
            shutil.rmtree(p)

@pytest.fixture
def temp_project():
    """Fixture que cria um projeto temporário para testes e o remove depois"""
    name = "test_project_pytest"
    password = "test_password_123"
    p = Project(name, password)
    
    # Limpeza preventiva
    if p.path.exists():
        p.delete_project()
        
    p.new_project()
    yield p
    
    if p.path.exists():
        p.delete_project()
