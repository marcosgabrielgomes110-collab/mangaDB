# Ponto de entrada principal do MangaDB
import sys
from pathlib import Path

# Configura o cache centralizado antes de importar modulos locais
PROJECT_ROOT = Path(__file__).resolve().parent
CACHEPATH = PROJECT_ROOT / "DATA" / "CACHE"
if not CACHEPATH.exists():
    CACHEPATH.mkdir(parents=True, exist_ok=True)
sys.pycache_prefix = str(CACHEPATH)

from src.cli.shell import MangaShell


def main():
    """Inicializa e executa o shell do banco de dados"""
    shell = MangaShell()
    shell.run()

if __name__ == "__main__":
    main()