import logging
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.pycmd2.git.git_add import get_changed_files_info
from src.pycmd2.git.git_add import GitAddFileStatus
from src.pycmd2.git.git_add import main


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    with patch("subprocess.run") as mock:
        mock.return_value = MagicMock(
            stdout="A  new.txt\nM  modified.txt\n?? untracked.txt\nD  deleted.txt\nMM conflicted.txt\nR  renamed.txt\nC  copied.txt\nU  unmerged.txt",  # noqa: E501
            returncode=0,
        )
        yield mock


@pytest.fixture
def mock_cli(tmp_path: Path) -> Generator[MagicMock, None, None]:
    with patch("src.pycmd2.git.git_add.cli") as mock:
        mock.cwd = str(tmp_path)
        mock.run_cmd = MagicMock()
        yield mock


@pytest.fixture
def mock_os_chdir() -> Generator[MagicMock, None, None]:
    with patch("os.chdir") as mock:
        yield mock


def test_git_add_file_status() -> None:
    # 测试GitAddFileStatus类
    status = GitAddFileStatus("A", Path("test.txt"))
    assert status.status == "A"
    assert str(status.filepath) == "test.txt"
    assert hash(status) == hash(("A", "test.txt"))


def test_get_changed_files_info(mock_subprocess: MagicMock) -> None:
    # 测试获取变更文件信息
    mock_subprocess.return_value.stdout = "A  new.txt\nM  modified.txt"
    files = get_changed_files_info()
    assert len(files) == 2  # noqa: PLR2004
    assert GitAddFileStatus("A", Path("new.txt")) in files
    assert GitAddFileStatus("M", Path("modified.txt")) in files

    mock_subprocess.assert_called_once_with(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_main_with_added_files(
    mock_cli: MagicMock,
    mock_subprocess: MagicMock,
    mock_os_chdir: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # 测试有新增文件的情况
    mock_subprocess.side_effect = [
        MagicMock(stdout="A  new.txt\n", returncode=0),
        MagicMock(stdout="A  new.txt\nM  modified.txt", returncode=0),
    ]

    with caplog.at_level(logging.INFO):
        main()

    # 验证命令执行

    mock_os_chdir.assert_called_once_with(mock_cli.cwd)
    mock_cli.run_cmd.assert_any_call(["git", "add", "."])
    # mock_cli.run_cmd.assert_any_call([
    #     "git",
    #     "commit",
    #     "-m",
    #     "新增文件: {'new'}",
    # ])

    # 验证日志输出
    assert "新增的文件" in caplog.text


def test_main_with_modified_files(
    mock_cli: MagicMock,
    mock_subprocess: MagicMock,
    mock_os_chdir: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # 测试有修改文件的情况
    mock_subprocess.side_effect = [
        MagicMock(stdout="M  modified.txt\n", returncode=0),
        MagicMock(stdout="M  modified.txt\nA  new.txt", returncode=0),
    ]

    with caplog.at_level(logging.INFO):
        main()

    # 验证命令执行
    mock_os_chdir.assert_called_once_with(mock_cli.cwd)
    mock_cli.run_cmd.assert_any_call(["git", "add", "."])
    # mock_cli.run_cmd.assert_any_call([
    #     "git",
    #     "commit",
    #     "-m",
    #     "修改文件: {'modified'}",
    # ])

    # 验证日志输出
    assert "修改的文件" in caplog.text


def test_main_with_no_changes(
    mock_cli: MagicMock,
    mock_subprocess: MagicMock,
    mock_os_chdir: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # 测试没有变更文件的情况
    mock_subprocess.side_effect = [
        MagicMock(stdout="", returncode=0),
        MagicMock(stdout="", returncode=0),
    ]

    with caplog.at_level(logging.WARNING):
        main()

    # 验证日志输出
    assert "没有新增的文件" in caplog.text
    assert "没有修改的文件" in caplog.text
    mock_os_chdir.assert_called_once_with(mock_cli.cwd)
