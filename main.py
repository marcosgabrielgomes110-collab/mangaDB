"""
aqui sera o ponto de partida do nosso banco de dados
um shell simples apenas para criar projetos e tabelas
crud completo
"""
from src.core.project import Project
from src.core.tables import Table
from src.core.utils import Colors, log_success, log_error, log_info, log_warning

def main():
    log_info("Digite 'help' para ver os comandos.")
    current_project = None
    
    while True:
        prefix = f" {Colors.OKGREEN}[{current_project.name}]{Colors.ENDC}" if current_project else ""
        try:
            prompt = input(f"{Colors.BOLD}mangaDB{prefix}>{Colors.ENDC} ").strip()
        except EOFError:
            break
        
        if not prompt:
            continue

        if prompt == "exit":
            log_info("Saindo...")
            break
            
        elif prompt == "help":
            print(f"""
{Colors.BOLD}Comandos Disponíveis:{Colors.ENDC}
  {Colors.OKBLUE}newp{Colors.ENDC}     - Criar novo projeto
  {Colors.OKBLUE}delp{Colors.ENDC}     - Deletar projeto
  {Colors.OKBLUE}openp{Colors.ENDC}    - Abrir projeto (exige senha)
  {Colors.OKBLUE}listp{Colors.ENDC}    - Listar todos os projetos
  {Colors.OKBLUE}newt{Colors.ENDC}     - Criar tabela (exige projeto aberto)
  {Colors.OKBLUE}listt{Colors.ENDC}    - Listar tabelas do projeto
  {Colors.OKBLUE}showt{Colors.ENDC}    - Mostrar conteúdo da tabela
  {Colors.OKBLUE}delt{Colors.ENDC}     - Deletar tabela
  {Colors.OKBLUE}clear{Colors.ENDC}    - Limpar terminal
  {Colors.OKBLUE}exit{Colors.ENDC}     - Sair
            """)

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
            
        elif prompt == "listp":
            p = Project("")
            p.list_projects()

        elif prompt == "clear":
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        
        # Comandos de Tabela (Exigem projeto aberto)
        elif prompt == "newt":
            if current_project:
                name = input("Nome da tabela: ")
                schema = {}
                print(f"{Colors.WARNING}Defina as colunas (deixe em branco para finalizar){Colors.ENDC}")
                while True:
                    col = input("Nome da coluna: ")
                    if not col:
                        break
                    tipo = input(f"Tipo da coluna '{col}': ")
                    schema[col] = tipo
                
                t = Table(current_project, name)
                t.create(schema)
                log_success(f"Tabela '{name}' criada!")
            else:
                log_error("Nenhum projeto aberto.")
        
        elif prompt == "listt":
            if current_project:
                tables = current_project.list_tables()
                log_info(f"Tabelas: {tables}")
            else:
                log_error("Nenhum projeto aberto.")

        elif prompt == "delt":
            if current_project:
                name = input("Nome da tabela: ")
                t = Table(current_project, name)
                t.delete()
            else:
                log_error("Nenhum projeto aberto.")

        elif prompt == "showt":
            if current_project:
                name = input("Nome da tabela: ")
                t = Table(current_project, name)
                try:
                    content = t.select()
                    print(f"\n{Colors.BOLD}Schema:{Colors.ENDC} {content['schema']}")
                    print(f"{Colors.OKCYAN}{'-' * 40}{Colors.ENDC}")
                    if not content['data']:
                        log_warning("Tabela sem dados.")
                    for i, row in enumerate(content['data']):
                        print(f"{Colors.BOLD}[{i}]{Colors.ENDC} {row}")
                    print(f"{Colors.OKCYAN}{'-' * 40}{Colors.ENDC}\n")
                except FileNotFoundError:
                    log_error(f"Tabela '{name}' não existe.")
            else:
                log_error("Nenhum projeto aberto.")
        else:
            log_warning(f"Comando '{prompt}' não reconhecido. Digite 'help'.")

if __name__ == "__main__":
    main()