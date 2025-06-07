from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.pycmd2.git.git_clean import main


@pytest.fixture
def mock_cli() -> Generator[MagicMock, None, None]:
    with patch("src.pycmd2.git.git_clean.cli") as mock:
        yield mock


@pytest.fixture
def mock_check_git_status() -> Generator[MagicMock, None, None]:
    with patch("src.pycmd2.git.git_clean.check_git_status") as mock:
        yield mock


def test_main_with_force(
    mock_cli: MagicMock,
    mock_check_git_status: MagicMock,
) -> None:
    # 测试强制清理模式
    main(force=True)

    # 验证命令执行
    mock_cli.run_cmd.assert_any_call([
        "git",
        "clean",
        "-xfd",
        "-e",
        ".venv",
    ])
    mock_cli.run_cmd.assert_any_call(["git", "checkout", "."])
    mock_check_git_status.assert_not_called()


def test_main_without_force_clean(
    mock_cli: MagicMock,
    mock_check_git_status: MagicMock,
) -> None:
    # 测试非强制模式且工作区干净
    mock_check_git_status.return_value = True
    main(force=False)

    # 验证命令执行
    mock_cli.run_cmd.assert_any_call([
        "git",
        "clean",
        "-xfd",
        "-e",
        ".venv",
    ])
    mock_cli.run_cmd.assert_any_call(["git", "checkout", "."])


def test_main_without_force_dirty(
    mock_cli: MagicMock,
    mock_check_git_status: MagicMock,
) -> None:
    # 测试非强制模式且工作区不干净
    mock_check_git_status.return_value = False
    main(force=False)

    # 验证没有执行清理命令
    mock_cli.run_cmd.assert_not_called()


def test_main_exclude_dirs(mock_cli: MagicMock) -> None:
    # 测试排除目录参数
    main(force=True)

    # 获取clean命令参数
    call_args = mock_cli.run_cmd.call_args_list[0][0][0]

    # 验证排除目录参数
    assert "-e" in call_args
    assert ".venv" in call_args
    assert call_args.index("-e") + 1 == call_args.index(".venv")
