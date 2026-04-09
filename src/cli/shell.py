# Gerenciamento do loop principal e despacho de comandos
import os
from src.cli.handlers import ProjectHandler, TableHandler, RecordHandler


class MangaShell:
    """Shell interativo"""

    def __init__(self):
        self.project = None

    def run(self):
        """Inicia o loop principal"""
        while True:
            prefix = f" [{self.project.name}]" if self.project else ""
            try:
                cmd = input(f"MangaDB{prefix}> ").strip()
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
        elif cmd == "home":
            if self.project:
                print(f"Projeto '{self.project.name}' fechado.")
                self.project = None
            else:
                print("Nenhum projeto aberto.")

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
                print("Nenhum projeto aberto.")
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
            print(f"Comando desconhecido: {cmd}. Digite 'help' para ver os comandos.")

    def _show_help(self):
        """Exibe comandos disponiveis"""
        print("  --- PROJETOS ---")
        print("  newp   - criar projeto")
        print("  delp   - deletar projeto")
        print("  openp  - abrir projeto")
        print("  listp  - listar projetos")
        print("  --- TABELAS ---")
        print("  newt   - criar tabela")
        print("  listt  - listar tabelas")
        print("  showt  - mostrar tabela")
        print("  delt   - deletar tabela")
        print("  --- REGISTROS ---")
        print("  insert - inserir registro")
        print("  query  - buscar registros")
        print("  update - atualizar registro")
        print("  delr   - deletar registro")
        print("  --- SISTEMA ---")
        print("  home   - fechar projeto (voltar ao inicio)")
        print("  clear  - limpar tela")
        print("  exit   - sair")
