import pytest
from src.core.utils import validate_name, log_success, log_error, log_info, log_warning


class TestValidateName:
    def test_valid_names(self):
        assert validate_name("projeto1") is True
        assert validate_name("my_project") is True
        assert validate_name("a") is True

    def test_invalid_names(self):
        assert validate_name("") is False
        assert validate_name("nome com espaco") is False
        assert validate_name("../escape") is False
        assert validate_name("nome\n") is False
        assert validate_name(".hidden") is False
        assert validate_name("a/b") is False
        assert validate_name(None) is False


class TestLogging:
    def test_log_functions_run(self, capsys):
        log_success("test ok")
        log_error("test error")
        log_info("test info")
        log_warning("test warn")
        captured = capsys.readouterr()
        assert "[OK]" in captured.out
        assert "[ERRO]" in captured.out
        assert "[INFO]" in captured.out
        assert "[AVISO]" in captured.out


class TestConfig:
    def test_get_config_creates_file(self, clean_config):
        from src.configs import get_config, CONFIGPATH
        config = get_config()
        assert config is not None
        assert "projects" in config
        assert config["projects"] == []

    def test_get_config_returns_none_on_corrupt(self, clean_config):
        from src.configs import CONFIGPATH, _CONFIG_LOCK
        with _CONFIG_LOCK:
            CONFIGPATH.write_text("not valid toml {{{")
        from src.configs import get_config
        config = get_config()
        assert config is None

    def test_save_and_get_config(self, clean_config):
        from src.configs import get_config, save_config, CONFIGPATH
        config = get_config()
        config["projects"].append({"name": "test", "id": "123"})
        save_config(config)

        loaded = get_config()
        assert len(loaded["projects"]) == 1
        assert loaded["projects"][0]["name"] == "test"

    def test_save_config_none(self, clean_config):
        from src.configs import save_config
        save_config(None)
