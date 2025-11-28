from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.client import get_client
from pycmd2.config import AttributeDiff
from pycmd2.config import TomlConfigMixin


class ExampleTestConfig(TomlConfigMixin):
    """Example config class."""

    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


cli = get_client()


class TestAttributeDiff:
    """Test attribute diff."""

    def test_attribute_diff(self) -> None:
        """Test attribute diff."""
        diff = AttributeDiff("foo", "bar", "baz")

        assert diff.attr == "foo"
        assert hash(diff)  # hashable


class TestConfig:
    """Test config class."""

    @pytest.fixture(autouse=True, scope="class")
    def fixture_clear_config(self) -> None:
        """Clear config files before each test."""
        ExampleTestConfig.clear()

    def test_config(self) -> None:
        """Test config class."""
        conf = ExampleTestConfig()
        assert conf.FOO == "bar"
        assert conf.BAZ == "qux"
        assert conf.NAME == "test"

        conf.setattr("FOO", "TEST")
        assert conf.FOO == "TEST"

        with pytest.raises(AttributeError) as execinfo:
            conf.setattr("INVALID_ATTR", 1)

        assert "Attribute INVALID_ATTR not found in" in str(execinfo.value)

        config_file = cli.settings_dir / "example_test.toml"
        assert config_file == conf._config_file  # noqa: SLF001

        assert not config_file.exists()  # Not exists until saved.
        conf.save()
        assert config_file.exists()

    def test_config_load(self) -> None:
        """Test config load."""
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("FOO = '123'\nBAZ = ['123', '456']")

        conf = ExampleTestConfig()
        assert conf.FOO == "123"
        assert isinstance(conf.BAZ, list)
        assert conf.BAZ == ["123", "456"]

    def test_config_load_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test config load error, use invalid file content."""
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("INVALID TOML CONTENT")

        conf = ExampleTestConfig()
        conf.load()

        assert "Read config error" in caplog.text
        assert "Expected '=' after a key in a key/value pair" in caplog.text

    @patch.object(Path, "exists", return_value=False)
    @patch.object(Path, "mkdir", return_value=None)
    def test_settings_dir_not_exist(
        self,
        mock_mkdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test settings dir not exist."""
        ExampleTestConfig()

        mock_exists.assert_called()
        mock_mkdir.assert_called_once()
