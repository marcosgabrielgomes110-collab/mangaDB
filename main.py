"""
shell simples para gerenciamento de projetos e tabelas
"""
import os
from src.core.project import Project
from src.core.tables import Table


def main():
    project = None

    while True:
        prefix = f" [{project.name}]" if project else ""
        try:
            cmd = input(f"mangaDB{prefix}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd == "exit":
            break

        elif cmd == "help":
            print("  newp   - criar projeto")
            print("  delp   - deletar projeto")
            print("  openp  - abrir projeto")
            print("  listp  - listar projetos")
            print("  newt   - criar tabela")
            print("  listt  - listar tabelas")
            print("  showt  - mostrar tabela")
            print("  delt   - deletar tabela")
            print("  clear  - limpar tela")
            print("  exit   - sair")

        elif cmd == "newp":
            name = input("Nome: ")
            password = input("Senha: ")
            p = Project(name, password)
            p.new_project()

        elif cmd == "delp":
            name = input("Nome: ")
            Project(name).delete_project()

        elif cmd == "openp":
            name = input("Nome: ")
            password = input("Senha: ")
            result = Project(name, password).open_project()
            if result:
                project = result

        elif cmd == "listp":
            Project.list_projects()

        elif cmd == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')

        # comandos que exigem projeto aberto
        elif cmd == "newt":
            if not project:
                print("Nenhum projeto aberto.")
                continue
            name = input("Nome da tabela: ")
            schema = {}
            print("Colunas (enter vazio para finalizar):")
            while True:
                col = input("  coluna: ")
                if not col:
                    break
                tipo = input("  tipo: ")
                schema[col] = tipo
            Table(project, name).create(schema)

        elif cmd == "listt":
            if not project:
                print("Nenhum projeto aberto.")
                continue
            tables = project.list_tables()
            if tables:
                for t in tables:
                    print(f"  {t}")
            else:
                print("Nenhuma tabela.")

        elif cmd == "showt":
            if not project:
                print("Nenhum projeto aberto.")
                continue
            name = input("Nome da tabela: ")
            try:
                content = Table(project, name).select()
                print(f"Schema: {content['schema']}")
                if not content["data"]:
                    print("Sem registros.")
                for i, row in enumerate(content["data"]):
                    print(f"  [{i}] {row}")
            except FileNotFoundError:
                print(f"Tabela '{name}' nao encontrada.")

        elif cmd == "delt":
            if not project:
                print("Nenhum projeto aberto.")
                continue
            name = input("Nome da tabela: ")
            Table(project, name).delete()

        else:
            print(f"Comando desconhecido: {cmd}")


if __name__ == "__main__":
    main()