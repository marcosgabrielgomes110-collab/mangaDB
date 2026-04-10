import os
import shutil
import uuid
from src.core.project import Project
from src.core.tables import Table
from src.configs import DATAPATH, get_config
from src.core.utils import Colors, log_info, log_success, log_error, log_warning

def run_tests():
    """Executa a suíte de testes robusta e verbosa para validar o banco"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}=== INICIANDO SUÍTE DE TESTES MANGADB ==={Colors.ENDC}")
    test_project_name = f"test_proj_{uuid.uuid4().hex[:8]}"
    test_password = "testpassword123"
    
    passed_tests = 0
    failed_tests = 0

    def assert_true(condition, msg):
        nonlocal passed_tests, failed_tests
        if condition:
            print(f"  {Colors.OKGREEN}[PASS]{Colors.ENDC} {msg}")
            passed_tests += 1
            return True
        else:
            print(f"  {Colors.FAIL}[FAIL]{Colors.ENDC} {msg}")
            failed_tests += 1
            return False

    try:
        # 1. Test Project Creation
        print(f"\n{Colors.BOLD}FASE 1: Gerenciamento de Projetos{Colors.ENDC}")
        p = Project(test_project_name, test_password)
        p.new_project()
        
        cfg = get_config()
        project_in_config = any(proj["name"] == test_project_name for proj in cfg.get("projects", []))
        project_dir_exists = (DATAPATH / test_project_name).exists()
        
        assert_true(project_in_config, "Projeto registrado no CONFIG.toml")
        assert_true(project_dir_exists, "Diretório do projeto criado")
        
        # 2. Test Project Authentication
        opened_p = Project(test_project_name, test_password).open_project()
        assert_true(opened_p is not None and opened_p.is_authenticated, "Autenticação de projeto via senha correta")
        
        wrong_p = Project(test_project_name, "wrongpass").open_project()
        assert_true(wrong_p is None, "Autenticação falha com senha errada")

        # 3. Test Table Creation & CRUD
        if opened_p:
            print(f"\n{Colors.BOLD}FASE 2: Tabelas e CRUD{Colors.ENDC}")
            table_name = "users_test"
            schema = {
                "username": {"type": "str", "encrypted": False},
                "age": {"type": "int", "encrypted": False},
                "secret_key": {"type": "str", "encrypted": True}
            }
            t = Table(opened_p, table_name)
            t.create(schema)
            assert_true(t.path.exists(), "Arquivo da tabela criado")
            
            record1 = {"username": "admin", "age": 30, "secret_key": "super_secret_1"}
            res = t.insert(record1, test_password)
            assert_true(res, "Inserção de registro válido efetuada")
            
            record2_invalid = {"username": "user", "age": "trinta", "secret_key": "sec"}
            res_invalid = t.insert(record2_invalid, test_password)
            assert_true(not res_invalid, "Validação falha ao inserir tipo incorreto")
            
            # 4. Test Encryption & Query
            print(f"\n{Colors.BOLD}FASE 3: Motor de Consulta e Criptografia{Colors.ENDC}")
            # Verificando arquivo bruto para ver se está críptico
            raw_data = t.show()["data"]
            assert_true(len(raw_data) == 1, "Tabela bruta contém 1 registro")
            assert_true(raw_data[0]["secret_key"] != "super_secret_1", "Campo 'secret_key' está criptografado no disco")
            
            # Verificando select
            results = t.select(test_password, where={"username": "admin"})
            assert_true(len(results) == 1, "Busca (where) por username funciona")
            assert_true(results[0]["secret_key"] == "super_secret_1", "Campo criptografado é descriptografado corretamente durante consulta")
            
            first_id = results[0]["_id"]
            
            # 5. Test Update
            print(f"\n{Colors.BOLD}FASE 4: Atualização de Dados{Colors.ENDC}")
            t.update_record(first_id, {"age": 31, "secret_key": "new_secret"}, test_password)
            updated_res = t.select(test_password, where={"_id": first_id})
            assert_true(updated_res[0]["age"] == 31, "Campo normal atualizado")
            assert_true(updated_res[0]["secret_key"] == "new_secret", "Campo criptografado atualizado")

            # 6. Test Delete
            print(f"\n{Colors.BOLD}FASE 5: Remoção Segura{Colors.ENDC}")
            t.delete_record(first_id)
            empty_res = t.select(test_password)
            assert_true(len(empty_res) == 0, "Registro completamente deletado")
            
            t.delete()
            assert_true(not t.path.exists(), "Tabela deletada do disco")
            
    finally:
        # Cleanup
        print(f"\n{Colors.BOLD}LIMPEZA{Colors.ENDC}")
        p_clean = Project(test_project_name)
        p_clean.delete_project()
        assert_true(not (DATAPATH / test_project_name).exists(), "Diretório de teste removido da persistência")
    
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}=== RESULTADO DOS TESTES ==={Colors.ENDC}")
    print(f"Total: {passed_tests + failed_tests} | Passou: {Colors.OKGREEN}{passed_tests}{Colors.ENDC} | Falhou: {Colors.FAIL}{failed_tests}{Colors.ENDC}")
    
    if failed_tests == 0:
        log_success("Todos os testes passaram com sucesso! O sistema está robusto.")
    else:
        log_error("Alguns testes falharam. Verifique os logs detalhados acima.")

if __name__ == "__main__":
    run_tests()
