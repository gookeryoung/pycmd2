import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from tests.test_config import ExampleTestConfig


@pytest.mark.slow
def test_config_save_toml(
    example_config: ExampleTestConfig,
    benchmark: BenchmarkFixture,
) -> None:
    """测试配置保存性能."""
    benchmark(example_config.save)
