from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.pycmd2.git.git_push_all import _get_cmd_full_path  # noqa: PLC2701
from src.pycmd2.git.git_push_all import check_git_status
from src.pycmd2.git.git_push_all import check_sensitive_data
from src.pycmd2.git.git_push_all import main
from src.pycmd2.git.git_push_all import push


@pytest.fixture
def mock_cli() -> Generator[MagicMock, None, None]:
    with patch("src.pycmd2.git.git_push_all.cli") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    with patch("subprocess.run") as mock:
        yield mock


def test_get_cmd_full_path_success() -> None:
    with patch("shutil.which", return_value="/usr/bin/git"):
        assert _get_cmd_full_path("git") == "/usr/bin/git"


def test_get_cmd_full_path_failure(mocker: MagicMock) -> None:
    mocker.patch("shutil.which", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        _get_cmd_full_path("nonexistent")


def test_check_git_status_clean(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = ""
    assert check_git_status() is True


def test_check_git_status_dirty(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = " M file.txt"
    assert check_git_status() is False


def test_check_sensitive_data_clean(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = "file.txt"
    assert check_sensitive_data() is True


def test_check_sensitive_data_dirty(mock_subprocess_run: MagicMock) -> None:
    mock_subprocess_run.return_value.stdout = ".env"
    assert check_sensitive_data() is False


def test_push_success(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.return_value.stdout = ""
    push("origin")
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "origin"])


def test_push_with_dirty_status(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.return_value.stdout = " M file.txt"
    push("origin")
    assert mock_cli.run_cmd.call_count == 0


def test_push_with_sensitive_data(
    mock_cli: MagicMock,
    mock_subprocess_run: MagicMock,
) -> None:
    mock_subprocess_run.side_effect = [
        MagicMock(stdout=""),  # check_git_status
        MagicMock(stdout=".env"),  # check_sensitive_data
    ]
    push("origin")
    assert mock_cli.run_cmd.call_count == 0


def test_main(mock_cli: MagicMock) -> None:
    main()
    mock_cli.run.assert_called_once()
