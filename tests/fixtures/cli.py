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
    """Mock subprocess.run().

    Args:
        mocker (MagicMock): Mocker.

    Returns:
        MagicMock: Mock subprocess.run().
    """
    return mocker.patch("subprocess.run")
