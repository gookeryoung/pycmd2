from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner


@pytest.fixture
def typer_runner() -> CliRunner:
    """Typer CLI 测试工具.

    Returns:
        CliRunner: Typer CLI 测试工具.
    """
    return CliRunner()


@pytest.fixture
def mock_subprocess_run(mocker: MagicMock) -> MagicMock:
    """模拟 subprocess.run().

    Args:
        mocker (MagicMock): 模拟器.

    Returns:
        MagicMock: 模拟 subprocess.run().
    """
    return mocker.patch("subprocess.run")
