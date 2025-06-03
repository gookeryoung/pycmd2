from pathlib import Path

import pytest

from pycmd2.common.cli import Client
from pycmd2.common.cli import get_client
from pycmd2.common.config import TomlConfigMixin


class ExampleConfig(TomlConfigMixin):
    """Example config class."""

    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


@pytest.fixture(scope="function", autouse=True)
def clear_config():
    config_files = list(Client.SETTINGS_DIR.glob("*.toml"))
    for config_file in config_files:
        config_file.unlink()


def test_config():
    conf = ExampleConfig()
    assert conf.FOO == "bar"
    assert conf.BAZ == "qux"
    assert conf.NAME == "test"

    config_file = Client.SETTINGS_DIR / "example.toml"
    assert config_file == conf._config_file

    assert not config_file.exists()
    conf._save()
    assert config_file.exists()


def test_config_load():
    config_file = Client.SETTINGS_DIR / "example.toml"
    config_file.write_text("FOO = '123'")

    conf = ExampleConfig()
    assert conf.FOO == "123"


def test_config_load_error(caplog):
    # 模拟文件存在但内容不是有效TOML的情况
    config_file = Client.SETTINGS_DIR / "example.toml"
    config_file.write_text("INVALID TOML CONTENT")

    conf = ExampleConfig()
    conf._load()

    assert "载入配置错误" in caplog.text
    assert "Expected '=' after a key in a key/value pair" in caplog.text


def test_config_save_error(mocker, caplog):
    invalid_path = Path("C:") if get_client().IS_WINDOWS else "/root/readonly"
    mocker.patch("pycmd2.common.cli.Client.SETTINGS_DIR", invalid_path)

    conf = ExampleConfig()
    conf._save()
    assert "保存配置错误" in caplog.text
