from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.commands.dev.gittools.git_push_all import _check_git_status  # noqa: PLC2701
from pycmd2.commands.dev.gittools.git_push_all import _check_sensitive_data  # noqa: PLC2701
from pycmd2.commands.dev.gittools.git_push_all import _get_cmd_full_path  # noqa: PLC2701
from pycmd2.commands.dev.gittools.git_push_all import git_push


@pytest.fixture
def mock_cli(mocker: MagicMock) -> MagicMock:
    return mocker.patch("pycmd2.commands.dev.gittools.git_push_all.cli")


def test_get_cmd_full_path_success() -> None:
    with patch("shutil.which", return_value="/usr/bin/git"):
        assert _get_cmd_full_path("git") == "/usr/bin/git"


def test_get_cmd_full_path_failure(mocker: MagicMock) -> None:
    mocker.patch("shutil.which", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        _get_cmd_full_path("nonexistent")


def test_check_git_status_clean(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = ""
    assert _check_git_status() is True


def test_check_git_status_dirty(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = " M file.txt"
    assert _check_git_status() is False


def test_check_sensitive_data_clean(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = "file.txt"
    assert _check_sensitive_data() is True


def test_check_sensitive_data_dirty(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = ".env"
    assert _check_sensitive_data() is False


def test_push_success(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.return_value.stdout = ""
    git_push("origin")
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "origin"])


def test_push_with_dirty_status(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.return_value.stdout = " M file.txt"
    git_push("origin")
    assert mock_cli.run_cmd.call_count == 0


def test_push_with_sensitive_data(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.side_effect = [
        MagicMock(stdout=""),  # check_git_status
        MagicMock(stdout=".env"),  # check_sensitive_data
    ]
    git_push("origin")
    assert mock_cli.run_cmd.call_count == 0
