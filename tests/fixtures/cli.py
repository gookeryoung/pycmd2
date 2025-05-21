import pytest
from typer.testing import CliRunner


@pytest.fixture
def typer_runner() -> CliRunner:
    """Typer CLI 测试工具"""
    return CliRunner()
