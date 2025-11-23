from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.commands.dev.gittools.git_init import GitInitRunner


@pytest.fixture
def mock_cli(tmp_path: Path) -> Generator[MagicMock, None, None]:
    with patch("pycmd2.commands.runner.cli") as mock:
        mock.cwd = str(tmp_path)
        yield mock


def test_main_command_sequence(mock_cli: MagicMock) -> None:
    # 测试命令执行顺序
    GitInitRunner().run()

    # 验证命令执行顺序和参数
    calls = mock_cli.run_cmd.call_args_list
    assert len(calls) == 3  # noqa: PLR2004

    # 验证git init
    assert calls[0][0][0] == ["git", "init"]

    # 验证git add
    assert calls[1][0][0] == ["git", "add", "."]

    # 验证git commit
    assert calls[2][0][0] == ["git", "commit", "-m", "initial commit"]


def test_main_directory_change() -> None:
    # 测试目录切换
    with patch("os.chdir") as mock_chdir:
        GitInitRunner().run()
        mock_chdir.assert_called_once()


def test_main_with_mock_commands(mock_cli: MagicMock) -> None:
    # 测试命令执行
    GitInitRunner().run()
    assert mock_cli.run_cmd.call_count == 3  # noqa: PLR2004
