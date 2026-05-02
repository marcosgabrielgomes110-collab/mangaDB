import os
from src.core.project import Project
from src.core.tables import Table
from src.core.utils import log_success, log_error, log_info
from src.cli.widgets import (
    console, input_text, input_confirm, input_table_name,
    show_schema_table, show_records_table, show_command_result,
    show_stats_table, make_panel,
)
from src.cli.theme import Theme, PANEL_BORDER


def convert_value(raw, col_type):
    try:
        if col_type in ("int", "number"):
            v = raw.replace(',', '.')
            return int(v) if ('.' not in v and 'e' not in v.lower()) else float(v)
        if col_type == "float":
            return float(raw)
        if col_type in ("bool", "boolean"):
            return raw.lower() in ("true", "1", "sim", "s")
        return raw
    except ValueError:
        return None


def find_record_id(table, partial_id):
    data = table.show().get("data", [])
    matches = [r for r in data if r.get("_id", "").startswith(partial_id)]

    if len(matches) == 1:
        return matches[0]["_id"]
    if len(matches) == 0:
        console.print("[red bold]Registro nao encontrado.[/]")
    else:
        console.print("[orange1]ID ambiguo, forneca mais caracteres.[/]")
    return None


class ProjectHandler:
    @staticmethod
    def create():
        name = input_text("Nome")
        password = input_text("Senha de autenticacao", password=True)
        enc_password = input_text("Senha de criptografia", password=True, default="")
        if not enc_password:
            enc_password = password
        Project(name, password, enc_password).new_project()

    @staticmethod
    def delete():
        name = input_text("Nome")
        password = input_text("Senha de autenticacao", password=True)
        if not input_confirm(f"Tem certeza que deseja deletar o projeto '{name}'?"):
            return
        Project(name, password).delete_project()

    @staticmethod
    def open():
        name = input_text("Nome")
        password = input_text("Senha de autenticacao", password=True)
        enc_password = input_text("Senha de criptografia", password=True, default="")
        if not enc_password:
            enc_password = password
        return Project(name, password, enc_password).open_project()

    @staticmethod
    def list():
        Project.list_projects()


class TableHandler:
    @staticmethod
    def create(project):
        name = input_text("Nome da tabela")
        schema = {}
        console.print("[gold1]Colunas (deixe em branco para finalizar):[/]")
        while True:
            col = input_text("  coluna")
            if not col:
                break
            tipo = input_text(f"  tipo de '{col}'")
            encrypted = input_text(f"  criptografar '{col}'? (s/N)").lower().strip() == 's'
            schema[col] = {"type": tipo, "encrypted": encrypted}
        Table(project, name).create(schema)

    @staticmethod
    def list(project):
        tables = project.list_tables()
        if not tables:
            console.print("[gold1]Nenhuma tabela encontrada neste projeto.[/]")
            return
        from src.cli.widgets import make_table
        table = make_table(title="Tabelas", headers=["Nome"])
        for t in tables:
            table.add_row(t)
        console.print(make_panel(table, border_style=PANEL_BORDER))

    @staticmethod
    def show(project):
        name = input_text("Nome da tabela")
        try:
            content = Table(project, name).show()
            schema = content["schema"]
            console.print(show_schema_table(schema))
            data = content.get("data", [])
            if not data:
                console.print("[gold1]Tabela sem registros.[/]")
            else:
                table = show_records_table(data, title=f"Dados - {name}")
                if table:
                    console.print(make_panel(table, border_style=PANEL_BORDER))
        except FileNotFoundError:
            console.print(f"[red bold]Tabela '{name}' nao encontrada.[/]")

    @staticmethod
    def delete(project):
        name = input_text("Nome da tabela")
        if not input_confirm(f"Tem certeza que deseja deletar a tabela '{name}'?"):
            return
        Table(project, name).delete()


class RecordHandler:
    @staticmethod
    def insert(project):
        name = input_text("Tabela")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            console.print(f"[red bold]Tabela '{name}' nao encontrada.[/]")
            return

        record = {}
        for col, info in schema.items():
            col_type = info["type"]
            raw = input_text(f"  {col} ({col_type})")
            value = convert_value(raw, col_type)
            if value is None:
                console.print(f"[red bold]Valor invalido para o tipo '{col_type}'.[/]")
                return
            record[col] = value

        if t.insert(record, project.enc_password):
            console.print("[green bold]Registro inserido com sucesso.[/]")

    @staticmethod
    def query(project):
        name = input_text("Tabela")
        try:
            t = Table(project, name)
        except FileNotFoundError:
            console.print(f"[red bold]Tabela '{name}' nao encontrada.[/]")
            return

        from src.core.query import parse_query
        console.print("[dark_goldenrod italic]Operadores: = != > < >= <= LIKE STARTS ENDS IN BETWEEN[/]")
        console.print("[dark_goldenrod italic]Combinacao: use AND ou virgula (ex: idade>18 AND nome LIKE Mar)[/]")
        filtro = input_text("Filtro (vazio para todos)")

        if not filtro:
            results = t.select(project.enc_password)
        else:
            conditions = parse_query(filtro)
            if not conditions:
                console.print("[red bold]Expressao de filtro invalida.[/]")
                return
            results = t.select(project.enc_password, conditions=conditions)

        if not results:
            console.print("[gold1]Nenhum resultado encontrado.[/]")
        else:
            console.print(f"[gold1]{len(results)} registro(s) encontrado(s):[/]")
            table = show_records_table(results, title=f"Resultados - {name}")
            if table:
                console.print(make_panel(table, border_style=PANEL_BORDER))

    @staticmethod
    def update(project):
        name = input_text("Tabela")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            console.print(f"[red bold]Tabela '{name}' nao encontrada.[/]")
            return

        partial = input_text("ID do registro")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        updates = {}
        console.print("[gold1]Campos (deixe em branco para finalizar):[/]")
        while True:
            campo = input_text("  campo")
            if not campo:
                break
            if campo not in schema:
                console.print(f"[orange1]Campo '{campo}' nao existe no schema.[/]")
                continue
            valor = input_text(f"  valor ({schema[campo]['type']})")
            converted = convert_value(valor, schema[campo]["type"])
            if converted is None:
                console.print(f"[red bold]Valor invalido para '{schema[campo]['type']}'.[/]")
                continue
            updates[campo] = converted

        if updates and t.update_record(record_id, updates, project.enc_password):
            console.print("[green bold]Registro atualizado com sucesso.[/]")

    @staticmethod
    def delete(project):
        name = input_text("Tabela")
        try:
            t = Table(project, name)
        except FileNotFoundError:
            console.print(f"[red bold]Tabela '{name}' nao encontrada.[/]")
            return

        partial = input_text("ID do registro")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        if not input_confirm(f"Tem certeza que deseja deletar o registro '{partial}'?"):
            return

        if t.delete_record(record_id):
            console.print("[green bold]Registro removido com sucesso.[/]")


class SystemHandler:
    @staticmethod
    def show_stats(project=None):
        from src.configs import get_config
        config = get_config()
        console.print(show_stats_table(project))

    @staticmethod
    def start_server():
        import subprocess
        import sys
        import time
        from src.configs import DATAPATH, API_HOST, API_PORT

        pid_file = DATAPATH / "api.pid"

        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0)
                console.print(f"[orange1]Servidor ja parece estar rodando (PID: {pid}).[/]")
                return
            except (ProcessLookupError, ValueError):
                pid_file.unlink()

        console.print(f"[gold1]Iniciando MangaDB Web API em background ({API_HOST}:{API_PORT})...[/]")

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "src.api.app"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time.sleep(1.5)
            if process.poll() is not None:
                console.print("[red bold]Servidor falhou ao iniciar. Verifique se a porta esta disponivel.[/]")
                return
            pid_file.write_text(str(process.pid))
            console.print(f"[green bold]Servidor iniciado com sucesso! (PID: {process.pid})[/]")
            console.print(f"[gold1]Acesse: http://{API_HOST}:{API_PORT}/docs para documentacao.[/]")
        except Exception as e:
            console.print(f"[red bold]Erro ao iniciar servidor: {e}[/]")

    @staticmethod
    def stop_server():
        from src.configs import DATAPATH
        pid_file = DATAPATH / "api.pid"

        if not pid_file.exists():
            console.print("[red bold]Arquivo de PID nao encontrado. O servidor esta rodando?[/]")
            return

        try:
            pid = int(pid_file.read_text())
            os.kill(pid, 15)
            pid_file.unlink()
            console.print(f"[green bold]Servidor (PID: {pid}) parado com sucesso.[/]")
        except ProcessLookupError:
            console.print("[red bold]Processo nao encontrado. Limpando arquivo de PID residual.[/]")
            pid_file.unlink()
        except Exception as e:
            console.print(f"[red bold]Erro ao parar servidor: {e}[/]")

    @staticmethod
    def server_status():
        from src.configs import DATAPATH, API_HOST, API_PORT
        pid_file = DATAPATH / "api.pid"

        status_str = "OFFLINE"
        status_style = "red bold"
        pid_info = ""

        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0)
                status_str = "ONLINE"
                status_style = "green bold"
                pid_info = f" (PID: {pid})"
            except (ProcessLookupError, ValueError):
                pass

        from src.cli.widgets import make_table
        table = make_table(title="Status da API Web", headers=["Item", "Valor"])
        table.add_row("Status", f"[{status_style}]{status_str}[/]{pid_info}")
        table.add_row("URL Base", f"http://{API_HOST}:{API_PORT}")
        if status_str == "ONLINE":
            table.add_row("Documentacao", f"http://{API_HOST}:{API_PORT}/docs")
        from src.cli.theme import make_panel
        console.print(make_panel(table, border_style=PANEL_BORDER))

        if status_str == "ONLINE":
            endpoints = make_table(title="Endpoints", headers=["Metodo", "Rota"])
            endpoints.add_row("POST", "/projects/{project}/auth")
            endpoints.add_row("GET", "/projects/{project}/tables")
            endpoints.add_row("POST", "/projects/{project}/tables/{table}/insert")
            endpoints.add_row("POST", "/projects/{project}/tables/{table}/query")
            endpoints.add_row("PUT", "/projects/{project}/tables/{table}/{id}")
            endpoints.add_row("DELETE", "/projects/{project}/tables/{table}/{id}")
            console.print(make_panel(endpoints, border_style=PANEL_BORDER))
