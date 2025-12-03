import re

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pycmd2.config import _to_snake_case  # noqa: PLC2701


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
    min_rounds=10,
    max_time=0.1,
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
