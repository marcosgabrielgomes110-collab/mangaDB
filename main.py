"""
aqui sera o ponto de partida do nosso banco de dados
um shell simples apenas para criar projetos e tabelas
crud completo
"""
from src.core.project import Project

def main():
    current_project = None
    while True:
        prefix = f" [{current_project.name}]" if current_project else ""
        prompt = input(f"mangaDB{prefix}> ")
        
        if prompt == "exit":
            break
        elif prompt == "newp":
            name = input("Nome do projeto: ")
            password = input("Senha do projeto: ")
            p = Project(name, password)
            p.new_project()
        elif prompt == "delp":
            name = input("Nome do projeto: ")
            p = Project(name)
            p.delete_project()
        elif prompt == "openp":
            name = input("Nome do projeto: ")
            password = input("Senha do projeto: ")
            p = Project(name, password)
            current_project = p.open_project()
        

if __name__ == "__main__":
    main()