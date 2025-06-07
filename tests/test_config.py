from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pycmd2.common.cli import get_client
from pycmd2.common.config import TomlConfigMixin


class ExampleConfig(TomlConfigMixin):
    """Example config class."""

    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


cli = get_client()


@pytest.fixture(autouse=True)
def clear_config() -> None:
    config_files = list(cli.settings_dir.glob("*.toml"))
    for config_file in config_files:
        config_file.unlink()


def test_config() -> None:
    conf = ExampleConfig()
    assert conf.FOO == "bar"
    assert conf.BAZ == "qux"
    assert conf.NAME == "test"

    config_file = cli.settings_dir / "example.toml"
    assert config_file == conf._config_file  # noqa: SLF001

    assert not config_file.exists()
    conf._save()  # noqa: SLF001
    assert config_file.exists()


def test_config_load() -> None:
    config_file = cli.settings_dir / "example.toml"
    config_file.write_text("FOO = '123'")

    conf = ExampleConfig()
    assert conf.FOO == "123"


def test_config_load_error(caplog: pytest.LogCaptureFixture) -> None:
    # 模拟文件存在但内容不是有效TOML的情况
    config_file = cli.settings_dir / "example.toml"
    config_file.write_text("INVALID TOML CONTENT")

    conf = ExampleConfig()
    conf._load()  # noqa: SLF001

    assert "读取配置错误" in caplog.text
    assert "Expected '=' after a key in a key/value pair" in caplog.text


def test_config_save_error(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    invalid_path = Path("C:") if cli.is_windows else "/root/readonly"
    mocker.patch("pycmd2.common.cli.Client.settings_dir", invalid_path)

    conf = ExampleConfig()
    conf._save()  # noqa: SLF001
    assert "未找到配置文件" in caplog.text
