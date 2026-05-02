import os
import shutil
from rich.rule import Rule
from rich.text import Text

from src.cli.theme import Theme, console, make_panel, PANEL_BORDER
from src.cli.widgets import show_banner, show_help
from src.cli.handlers import ProjectHandler, TableHandler, RecordHandler, SystemHandler


class MangaApp:
    def __init__(self):
        self.project = None

    def run(self):
        show_banner()
        while True:
            self._show_prompt()
            try:
                cmd = console.input().strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                break

            if not cmd:
                continue
            if cmd == "exit":
                console.print("\n[dark_goldenrod]MangaDB encerrado.[/]")
                break

            self._dispatch(cmd)

    def _show_prompt(self):
        if self.project:
            prompt_text = Text.assemble(
                Text("MangaDB", style="dark_orange bold"),
                Text(f" [{self.project.name}]", style="gold1 bold"),
                Text(" > ", style="dark_orange bold"),
            )
        else:
            prompt_text = Text("MangaDB > ", style="dark_orange bold")
        console.print(prompt_text, end="")

    def _dispatch(self, cmd):
        if cmd == "help":
            show_help()

        elif cmd == "clear":
            os.system('clear' if os.name == 'posix' else 'cls')
            show_banner()

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
                console.print("[orange1]Uso: server [start|stop|status][/]")

        elif cmd == "home":
            if self.project:
                console.print(f"[gold1]Projeto '{self.project.name}' fechado.[/]")
                self.project = None
            else:
                console.print("[gold1]Voce ja esta na home.[/]")

        elif cmd == "test":
            console.print("[gold1]Iniciando suite de testes (Pytest)...[/]")
            os.system("pytest -v")

        elif cmd == "clearcache":
            from src.configs import clear_cache
            if clear_cache():
                console.print("[green bold]Cache do sistema limpo com sucesso.[/]")
            else:
                console.print("[red bold]Nao foi possivel limpar o cache (timeout no lock).[/]")

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

        elif cmd in ("newt", "listt", "showt", "delt", "insert", "query", "update", "delr"):
            if not self.project:
                console.print("[red bold]Erro: Nenhum projeto aberto.[/]")
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
            console.print(f"[orange1]Comando desconhecido: '{cmd}'. Digite 'help'.[/]")

        console.print(Rule(style=PANEL_BORDER))
