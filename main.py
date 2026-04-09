# Ponto de entrada principal do MangaDB
from src.cli.shell import MangaShell

def main():
    """Inicializa e executa o shell do banco de dados"""
    shell = MangaShell()
    shell.run()

if __name__ == "__main__":
    main()