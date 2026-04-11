# Gerenciamento do loop principal e despacho de comandos
import os
from src.cli.handlers import ProjectHandler, TableHandler, RecordHandler, SystemHandler
from src.core.utils import Colors, log_info, log_error, log_warning, log_success


class MangaShell:
    """Shell interativo"""

    def __init__(self):
        self.project = None

    def run(self):
        """Inicia o loop principal"""
        while True:
            # Prompt colorido: MangoDB em ciano, projeto em azul negrito
            p_name = f" {Colors.BOLD}{Colors.OKBLUE}[{self.project.name}]{Colors.ENDC}" if self.project else ""
            prompt = f"{Colors.BOLD}{Colors.OKCYAN}MangaDB{Colors.ENDC}{p_name}> "
            
            try:
                cmd = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not cmd:
                continue

            if cmd == "exit":
                break

            self._dispatch(cmd)

    def _dispatch(self, cmd):
        """Roteia o comando para o handler apropriado"""
        
        # Comandos de utilidade
        if cmd == "help":
            self._show_help()
        elif cmd == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd == "stats":
            SystemHandler.show_stats(self.project)
        elif cmd.startswith("server"):
            parts = cmd.split()
            sub = parts[1] if len(parts) > 1 else "status"
            
            if sub == "start":
                SystemHandler.start_server()
            elif sub == "stop":
                SystemHandler.stop_server()
            elif sub in ("status", "info"):
                SystemHandler.server_status()
            else:
                log_warning("Uso: server [start|stop|status]")
        elif cmd == "home":
            if self.project:
                log_info(f"Projeto '{self.project.name}' fechado.")
                self.project = None
            else:
                log_info("Você já está na home.")
        elif cmd == "test":
            log_info("Iniciando suíte de testes robusta (Pytest)...")
            os.system("pytest -v")
        elif cmd == "clearcache":
            import shutil
            from src.configs import CACHEPATH
            try:
                if CACHEPATH.exists():
                    shutil.rmtree(CACHEPATH, ignore_errors=True)
                CACHEPATH.mkdir(parents=True, exist_ok=True)
                log_success("Cache do sistema limpo com sucesso.")
            except Exception as e:
                log_error(f"Não foi possível limpar o cache: {e}")

        # Comandos de projeto
        elif cmd == "newp":
            ProjectHandler.create()
        elif cmd == "delp":
            ProjectHandler.delete()
        elif cmd == "openp":
            res = ProjectHandler.open()
            if res:
                self.project = res
        elif cmd == "listp":
            ProjectHandler.list()

        # Comandos que exigem projeto aberto
        elif cmd in ("newt", "listt", "showt", "delt", "insert", "query", "update", "delr"):
            if not self.project:
                log_error("Erro: Nenhum projeto aberto.")
                return

            if cmd == "newt":
                TableHandler.create(self.project)
            elif cmd == "listt":
                TableHandler.list(self.project)
            elif cmd == "showt":
                TableHandler.show(self.project)
            elif cmd == "delt":
                TableHandler.delete(self.project)
            elif cmd == "insert":
                RecordHandler.insert(self.project)
            elif cmd == "query":
                RecordHandler.query(self.project)
            elif cmd == "update":
                RecordHandler.update(self.project)
            elif cmd == "delr":
                RecordHandler.delete(self.project)
        else:
            log_warning(f"Comando desconhecido: '{cmd}'. Digite 'help'.")

    def _show_help(self):
        """Exibe comandos disponiveis com formatação limpa"""
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}COMANDOS DISPONÍVEIS{Colors.ENDC}")
        
        print(f"\n{Colors.OKBLUE}[ PROJETOS ]{Colors.ENDC}")
        print("  newp   - Criar novo projeto")
        print("  delp   - Deletar um projeto")
        print("  openp  - Abrir projeto existente")
        print("  listp  - Listar todos os projetos")
        
        print(f"\n{Colors.OKGREEN}[ TABELAS ]{Colors.ENDC}")
        print("  newt   - Criar nova tabela com schema")
        print("  listt  - Listar tabelas do projeto")
        print("  showt  - Visualizar schema e dados")
        print("  delt   - Deletar uma tabela")
        
        print(f"\n{Colors.WARNING}[ REGISTROS ]{Colors.ENDC}")
        print("  insert - Inserir novo registro")
        print("  query  - Buscar registros (filtros suportados)")
        print("  update - Atualizar registro por ID")
        print("  delr   - Deletar registro por ID")
        
        print(f"\n{Colors.OKCYAN}[ SISTEMA ]{Colors.ENDC}")
        print("  stats           - Estatísticas do banco/projeto")
        print("  server start    - Iniciar servidor (background)")
        print("  server stop     - Parar servidor (usando PID)")
        print("  server status   - Status e endpoints da API")
        print("  home            - Sair do projeto atual")
        print("  test            - Rodar suíte de testes (Pytest)")
        print("  clearcache      - Limpar o cache do sistema")
        print("  clear           - Limpar o terminal")
        print("  exit            - Fechar o MangaDB")
        print()
