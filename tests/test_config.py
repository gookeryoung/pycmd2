from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pycmd2.common.cli import get_client
from pycmd2.config import TomlConfigMixin


class ExampleTestConfig(TomlConfigMixin):
    """Example config class."""

    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


cli = get_client()


class TestConfig:
    """Test config class."""

    @pytest.fixture(autouse=True)
    def fixture_clear_config(self) -> None:
        """Clear config files before each test."""
        ExampleTestConfig.clear()

    def test_config(self) -> None:
        """Test config class."""
        conf = ExampleTestConfig()
        assert conf.FOO == "bar"
        assert conf.BAZ == "qux"
        assert conf.NAME == "test"

        config_file = cli.settings_dir / "example_test.toml"
        assert config_file == conf._config_file  # noqa: SLF001

        assert not config_file.exists()
        conf.save()
        assert config_file.exists()

    def test_config_load(self) -> None:
        """Test config load."""
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("FOO = '123'\nBAZ = ['123', '456']")

        conf = ExampleTestConfig()
        assert conf.FOO == "123"
        assert conf.BAZ == ["123", "456"]

    def test_config_load_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test config load error."""
        # 模拟文件存在但内容不是有效TOML的情况
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("INVALID TOML CONTENT")

        conf = ExampleTestConfig()
        conf.load()

        assert "Read config error" in caplog.text
        assert "Expected '=' after a key in a key/value pair" in caplog.text

    def test_config_save_error(
        self,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test config save error."""
        invalid_path = Path("C:") if cli.is_windows else "/root/readonly"
        mocker.patch("pycmd2.common.cli.Client.settings_dir", invalid_path)

        conf = ExampleTestConfig()
        conf.save()
        assert "Config file not found" in caplog.text
