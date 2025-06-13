import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from tests.test_config import ExampleConfig


@pytest.mark.slow
def test_config_save_toml(
    example_config: ExampleConfig,
    benchmark: BenchmarkFixture,
) -> None:
    benchmark(example_config._save)  # noqa: SLF001
