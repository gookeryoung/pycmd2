from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.client import get_client
from pycmd2.config import AttributeDiff
from pycmd2.config import TomlConfigMixin


class ExampleTestConfig(TomlConfigMixin):
    """示例配置类."""

    name = "test"
    foo = "bar"
    baz = "qux"


cli = get_client()


class TestAttributeDiff:
    """测试属性差异功能."""

    def test_attribute_diff(self) -> None:
        """测试属性差异."""
        diff = AttributeDiff("foo", "bar", "baz")

        assert diff.attr == "foo"
        assert hash(diff)  # 可哈希


class TestConfig:
    """测试配置类."""

    @pytest.fixture(autouse=True, scope="class")
    def fixture_clear_config(self) -> None:
        """在每个测试前清除配置文件."""
        ExampleTestConfig.clear()

    def test_config(self) -> None:
        """测试配置类."""
        conf = ExampleTestConfig()
        assert conf.foo == "bar"
        assert conf.baz == "qux"
        assert conf.name == "test"

        conf.setattr("foo", "TEST")
        assert conf.foo == "TEST"

        with pytest.raises(AttributeError) as execinfo:
            conf.setattr("INVALID_ATTR", 1)

        assert "属性 INVALID_ATTR 在 ExampleTestConfig 中不存在" in str(execinfo.value)

        config_file = cli.settings_dir / "example_test.toml"
        assert config_file == conf._config_file  # noqa: SLF001

        assert not config_file.exists()  # 保存前不存在
        conf.save()
        assert config_file.exists()

    def test_config_load(self) -> None:
        """测试配置加载."""
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("foo = '123'\nbaz = ['123', '456']")

        conf = ExampleTestConfig()
        assert conf.foo == "123"
        assert isinstance(conf.baz, list)
        assert conf.baz == ["123", "456"]

    def test_config_load_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """测试配置加载错误, 使用无效文件内容."""
        config_file = cli.settings_dir / "example_test.toml"
        config_file.write_text("INVALID TOML CONTENT")

        conf = ExampleTestConfig()
        conf.load()

        assert "读取配置失败" in caplog.text
        assert "Expected '=' after a key in a key/value pair" in caplog.text

    @patch.object(Path, "exists", return_value=False)
    @patch.object(Path, "mkdir", return_value=None)
    def test_settings_dir_not_exist(
        self,
        mock_mkdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """测试设置目录不存在."""
        ExampleTestConfig()

        mock_exists.assert_called()
        mock_mkdir.assert_called_once()

    @patch.object(Path, "exists", return_value=True)
    def test_get_instance(self, mock_exists: MagicMock) -> None:  # noqa: ARG002
        """测试获取实例."""
        conf1 = ExampleTestConfig.get_instance()
        conf2 = ExampleTestConfig.get_instance()

        assert conf1 == conf2
