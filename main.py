"""
aqui sera o ponto de partida do nosso banco de dados
um shell simples apenas para criar projetos e tabelas
crud completo
"""
from src.core.project import Project

def main():
    while True:
        prompt = input("mangaDB> ")
        if prompt == "exit":
            break
        elif prompt == "newp":
            name = input("Nome do projeto: ")
            p = Project(name)
            p.new_project()
        elif prompt == "delp":
            name = input("Nome do projeto: ")
            p = Project(name)
            p.delete_project()
        

if __name__ == "__main__":
    main()