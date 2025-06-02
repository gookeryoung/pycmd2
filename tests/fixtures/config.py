import pytest

__all__ = [
    "example_config",
]


@pytest.fixture
def example_config():
    from pycmd2.common.config import TomlConfigMixin

    class ExampleConfig(TomlConfigMixin):
        NAME = "test"
        FOO = "bar"
        BAZ = "qux"

    return ExampleConfig()
