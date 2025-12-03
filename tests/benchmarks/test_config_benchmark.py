import re

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pycmd2.config import _to_snake_case  # noqa: PLC2701
from pycmd2.config import AdvancedOptimizedConfigMixin
from pycmd2.config import OptimizedTomlConfigMixin
from pycmd2.config import TomlConfigMixin


def _deprecated_to_snake_case(name: str) -> str:
    """将驼峰命名转换为下划线命名, 处理连续大写字母的情况.

    Args:
        name (str): 驼峰命名

    Returns:
        str: 下划线命名

    例如: "HTTPRequest" -> "http_request"
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # 处理连续大写字母的情况
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return name.lower()


@pytest.mark.benchmark(
    group="to_snake_case",
)
@pytest.mark.parametrize(
    "string",
    [
        "ThisIsATestString",
        "ThisIsAVeryLongTestString",
        "ThisIsATestStringWithManyWords",
        "ThisIsATestStringWithManyWordsAndNumbers1234567890",
        "ThisIsATestStringWithManyWordsAndNumbersAndSpecialCharacters1234567890!@#$%^&*()_+-=[]{};':\",./<>?`~",
    ],
)
class TestToSnakeCase:
    """测试 to_snake_case 函数性能."""

    def test_deprecated_to_snake_case(
        self,
        benchmark: BenchmarkFixture,
        string: str,
    ) -> None:
        """测试 to_snake_case 函数性能."""
        benchmark(_deprecated_to_snake_case, string)

    def test_optimized_to_snake_case(
        self,
        benchmark: BenchmarkFixture,
        string: str,
    ) -> None:
        """测试 optimized_to_snake_case 函数性能."""
        benchmark(_to_snake_case, string)


class OriginalConfig(TomlConfigMixin):
    """测试配置类."""

    name = "test"
    attr1 = "value1"
    attr2 = "value2"
    attr3 = 100


# 创建测试配置类
class OptimizedConfig(OptimizedTomlConfigMixin):
    """测试配置类."""

    name = "test"
    attr1 = "value1"
    attr2 = "value2"
    attr3 = 100


class AdvancedOptimizedConfig(AdvancedOptimizedConfigMixin):
    """测试配置类."""

    name = "test"
    attr1 = "value1"
    attr2 = "value2"
    attr3 = 100


@pytest.mark.benchmark(
    group="config_attribute_access",
    min_rounds=1000,
)
class TestConfigAttributeAccess:
    """测试配置属性访问性能."""

    def test_attribute_access(self, benchmark: BenchmarkFixture) -> None:
        """测试属性访问性能."""
        config = OriginalConfig()
        benchmark(config.getattr, "name")

    def test_optimized_attribute_access(self, benchmark: BenchmarkFixture) -> None:
        """测试优化后的属性访问性能."""
        config = OptimizedConfig()
        benchmark(config.getattr, "name")

    def test_advanced_optimized_attribute_access(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """测试优化后的属性访问性能."""
        config = AdvancedOptimizedConfig()
        benchmark(config.getattr, "name")
