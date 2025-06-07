import pytest

from pycmd2.common.config import TomlConfigMixin

__all__ = [
    "example_config",
]


class ExampleConfig(TomlConfigMixin):
    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


@pytest.fixture
def example_config() -> ExampleConfig:
    return ExampleConfig()
