import os
from src.core.project import Project
from src.core.tables import Table
from src.core.utils import log_success, log_error, log_info, log_warning, Colors


def convert_value(raw, col_type):
    """Converte input string para o tipo definido no schema"""
    try:
        if col_type in ("int", "number"):
            return int(raw) if "." not in raw else float(raw)
        if col_type == "float":
            return float(raw)
        if col_type in ("bool", "boolean"):
            return raw.lower() in ("true", "1", "sim", "s")
        return raw
    except ValueError:
        return None


def find_record_id(table, partial_id):
    """Resolve id parcial para id completo"""
    data = table.show()["data"]
    matches = [r for r in data if r.get("_id", "").startswith(partial_id)]

    if len(matches) == 1:
        return matches[0]["_id"]
    if len(matches) == 0:
        log_error("Registro nao encontrado.")
    else:
        log_warning("ID ambiguo, forneca mais caracteres.")
    return None


def display_record(rec):
    """Exibe registro ocultando campos internos"""
    rid = rec.get("_id", "?")[:8]
    campos = {k: v for k, v in rec.items() if not k.startswith("_")}
    print(f"  {Colors.BOLD}[{rid}]{Colors.ENDC} {campos}")


class ProjectHandler:
    @staticmethod
    def create():
        name = input("Nome: ")
        password = input("Senha de autenticacao: ")
        enc_password = input("Senha de criptografia (ENTER para usar a mesma): ")
        if not enc_password:
            enc_password = password
        Project(name, password, enc_password).new_project()

    @staticmethod
    def delete():
        name = input("Nome: ")
        password = input("Senha de autenticacao: ")
        Project(name, password).delete_project()

    @staticmethod
    def open():
        name = input("Nome: ")
        password = input("Senha de autenticacao: ")
        enc_password = input("Senha de criptografia (ENTER para usar a mesma): ")
        if not enc_password:
            enc_password = password
        return Project(name, password, enc_password).open_project()

    @staticmethod
    def list():
        Project.list_projects()


class TableHandler:
    @staticmethod
    def create(project):
        name = input("Nome da tabela: ")
        schema = {}
        print("Colunas (enter vazio para finalizar):")
        while True:
            col = input("  coluna: ")
            if not col:
                break
            tipo = input(f"  tipo de '{col}': ")
            encrypted = input(f"  criptografar '{col}'? (y/n): ").lower().strip() == 'y'
            schema[col] = {"type": tipo, "encrypted": encrypted}
        Table(project, name).create(schema)

    @staticmethod
    def list(project):
        tables = project.list_tables()
        if tables:
            log_info("Tabelas encontradas:")
            for t in tables:
                print(f"  {Colors.BOLD}- {t}{Colors.ENDC}")
        else:
            log_warning("Nenhuma tabela encontrada neste projeto.")

    @staticmethod
    def show(project):
        name = input("Nome da tabela: ")
        try:
            content = Table(project, name).show()
            schema = content["schema"]
            # Exibe o schema de forma clara com cores
            schema_parts = []
            for k, v in schema.items():
                enc_tag = f" {Colors.OKBLUE}(enc){Colors.ENDC}" if v['encrypted'] else ""
                schema_parts.append(f"{Colors.BOLD}{k}{Colors.ENDC}:{v['type']}{enc_tag}")
            
            print(f"{Colors.OKCYAN}Schema:{Colors.ENDC} {' | '.join(schema_parts)}")
            
            if not content["data"]:
                log_info("Tabela sem registros.")
            else:
                for rec in content["data"]:
                    display_record(rec)
        except FileNotFoundError:
            log_error(f"Tabela '{name}' nao encontrada.")

    @staticmethod
    def delete(project):
        name = input("Nome da tabela: ")
        Table(project, name).delete()


class RecordHandler:
    @staticmethod
    def insert(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            log_error(f"Tabela '{name}' nao encontrada.")
            return

        record = {}
        for col, info in schema.items():
            col_type = info["type"]
            raw = input(f"  {col} ({col_type}): ")
            value = convert_value(raw, col_type)
            if value is None:
                log_error(f"Valor invalido para o tipo '{col_type}'.")
                break
            record[col] = value
        else:
            if t.insert(record, project.enc_password):
                log_success("Registro inserido com sucesso.")

    @staticmethod
    def query(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            log_error(f"Tabela '{name}' nao encontrada.")
            return

        filtro = input("Filtro (campo=valor, vazio para todos): ").strip()
        where = None
        if filtro:
            parts = filtro.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                if key in schema:
                    val = convert_value(val, schema[key]["type"])
                where = {key: val}

        results = t.select(project.enc_password, where=where)
        if not results:
            log_info("Nenhum resultado encontrado.")
        else:
            for rec in results:
                display_record(rec)

    @staticmethod
    def update(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
            schema = t.show()["schema"]
        except FileNotFoundError:
            log_error(f"Tabela '{name}' nao encontrada.")
            return

        partial = input("ID do registro: ")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        updates = {}
        print("Campos (enter vazio para finalizar):")
        while True:
            campo = input("  campo: ")
            if not campo:
                break
            if campo not in schema:
                log_warning(f"Campo '{campo}' nao existe no schema.")
                continue
            valor = input("  valor: ")
            converted = convert_value(valor, schema[campo]["type"])
            if converted is None:
                log_error(f"Valor invalido para '{schema[campo]['type']}'.")
                continue
            updates[campo] = converted

        if updates and t.update_record(record_id, updates, project.enc_password):
            log_success("Registro atualizado com sucesso.")

    @staticmethod
    def delete(project):
        name = input("Tabela: ")
        try:
            t = Table(project, name)
        except FileNotFoundError:
            log_error(f"Tabela '{name}' nao encontrada.")
            return

        partial = input("ID do registro: ")
        record_id = find_record_id(t, partial)
        if not record_id:
            return

        if t.delete_record(record_id):
            log_success("Registro removido com sucesso.")


class SystemHandler:
    @staticmethod
    def show_stats(project=None):
        """Exibe estatísticas globais ou do projeto atual"""
        from src.configs import get_config
        config = get_config()
        
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}ESTATÍSTICAS DO SISTEMA{Colors.ENDC}")
        print(f"  Projetos registrados: {len(config['projects'])}")
        
        if project:
            print(f"\n{Colors.OKBLUE}[ PROJETO ATUAL: {project.name} ]{Colors.ENDC}")
            tables = project.list_tables()
            print(f"  Tabelas: {len(tables)}")
            total_records = 0
            for t_name in tables:
                t = Table(project, t_name)
                total_records += len(t.show()["data"])
            print(f"  Total de registros: {total_records}")
        print()

    @staticmethod
    def start_server():
        """Inicia a API Web em background e salva o PID"""
        import subprocess
        import sys
        import time
        from src.configs import DATAPATH, API_HOST, API_PORT
        
        pid_file = DATAPATH / "api.pid"
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0) # Verifica se processo existe
                log_warning(f"Servidor já parece estar rodando (PID: {pid}).")
                return
            except (ProcessLookupError, ValueError):
                pid_file.unlink()

        log_info(f"Iniciando MangaDB Web API em background ({API_HOST}:{API_PORT})...")
        
        try:
            # Roda como processo filho desacoplado
            process = subprocess.Popen(
                [sys.executable, "-m", "src.api.app"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            pid_file.write_text(str(process.pid))
            time.sleep(1) # Aguarda inicialização
            log_success(f"Servidor iniciado com sucesso! (PID: {process.pid})")
            log_info(f"Acesse: http://{API_HOST}:{API_PORT}/docs para documentação.")
        except Exception as e:
            log_error(f"Erro ao iniciar servidor: {e}")

    @staticmethod
    def stop_server():
        """Para o servidor usando o PID salvo"""
        from src.configs import DATAPATH
        pid_file = DATAPATH / "api.pid"
        
        if not pid_file.exists():
            log_error("Arquivo de PID não encontrado. O servidor está rodando?")
            return

        try:
            pid = int(pid_file.read_text())
            os.kill(pid, 15) # SIGTERM
            pid_file.unlink()
            log_success(f"Servidor (PID: {pid}) parado com sucesso.")
        except ProcessLookupError:
            log_error("Processo não encontrado. Limpando arquivo de PID residual.")
            pid_file.unlink()
        except Exception as e:
            log_error(f"Erro ao parar servidor: {e}")

    @staticmethod
    def server_status():
        """Verifica se o servidor está ativo e lista endpoints"""
        from src.configs import DATAPATH, API_HOST, API_PORT
        pid_file = DATAPATH / "api.pid"
        
        status = f"{Colors.FAIL}OFFLINE{Colors.ENDC}"
        pid_info = ""
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                os.kill(pid, 0)
                status = f"{Colors.OKGREEN}ONLINE{Colors.ENDC}"
                pid_info = f" (PID: {pid})"
            except (ProcessLookupError, ValueError):
                pass

        print(f"\n{Colors.BOLD}STATUS DA API WEB:{Colors.ENDC} {status}{pid_info}")
        print(f"URL Base: http://{API_HOST}:{API_PORT}")
        
        if "ONLINE" in status:
            print(f"\n{Colors.BOLD}ENDPOINTS DISPONÍVEIS:{Colors.ENDC}")
            print("  [POST]   /projects/{project}/auth")
            print("  [GET]    /projects/{project}/tables")
            print("  [POST]   /projects/{project}/tables/{table}/insert")
            print("  [POST]   /projects/{project}/tables/{table}/query")
            print("  [PUT]    /projects/{project}/tables/{table}/{id}")
            print("  [DELETE] /projects/{project}/tables/{table}/{id}")
            print(f"\n{Colors.OKCYAN}Documentação Swagger:{Colors.ENDC} http://{API_HOST}:{API_PORT}/docs")
        print()
