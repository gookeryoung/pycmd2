import pytest

from pycmd2.config import TomlConfigMixin

__all__ = [
    "example_config",
]


class ExampleConfig(TomlConfigMixin):
    """示例配置类."""

    NAME = "test"
    FOO = "bar"
    BAZ = "qux"


@pytest.fixture
def example_config() -> ExampleConfig:
    """示例配置.

    Returns:
        ExampleConfig: 示例配置实例.
    """
    return ExampleConfig()
