import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.commands.dev.gittools.git_init import GitInitRunner


@pytest.fixture
def mock_cli(tmp_path: Path) -> Generator[MagicMock, None, None]:
    with patch("pycmd2.commands.dev.gittools.git_init.cli") as mock:
        mock.cwd = tmp_path
        yield mock


@pytest.fixture
def isolated_tmpdir(tmp_path: Path) -> Generator[Path, None, None]:
    """创建一个完全隔离的临时目录用于git测试.

    Yields:
        Generator[Path, None, None]: 隔离的临时目录
    """
    git_test_dir = tmp_path / "git_test"
    git_test_dir.mkdir(exist_ok=True)
    original_cwd = Path.cwd()
    try:
        yield git_test_dir
    finally:
        # 确保恢复原始工作目录
        os.chdir(original_cwd)


def test_main_command_sequence(mock_cli: MagicMock, isolated_tmpdir: Path) -> None:
    """测试命令执行顺序, 确保在隔离的临时目录中运行."""
    # 在隔离目录中执行测试
    os.chdir(isolated_tmpdir)

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


def test_main_directory_change(mock_cli: MagicMock, isolated_tmpdir: Path) -> None:
    """测试目录切换, 确保不会影响到实际项目目录."""
    # 记录当前目录, 确保测试后恢复
    original_cwd = Path.cwd()

    try:
        # 测试目录切换
        with patch("os.chdir") as mock_chdir:
            GitInitRunner().run()
            mock_chdir.assert_called_once()

            # 验证切换到的是临时目录而不是项目目录
            args, _ = mock_chdir.call_args
            changed_dir = args[0]
            assert (
                str(isolated_tmpdir) in changed_dir or str(mock_cli.cwd) in changed_dir
            )
            assert original_cwd not in changed_dir  # 确保不是切换到项目目录
    finally:
        # 确保恢复原始工作目录
        os.chdir(original_cwd)


def test_main_with_mock_commands(mock_cli: MagicMock, isolated_tmpdir: Path) -> None:
    """测试命令执行, 确保在隔离环境中运行."""
    # 在隔离目录中执行测试
    os.chdir(isolated_tmpdir)

    # 测试命令执行
    GitInitRunner().run()
    assert mock_cli.run_cmd.call_count == 3  # noqa: PLR2004


def test_git_initialization_in_isolated_environment(isolated_tmpdir: Path) -> None:
    """测试git初始化完全在隔离环境中进行, 不影响项目目录."""
    # 确保不在项目目录中
    original_cwd = Path.cwd()
    orignal_files = {f.name for f in original_cwd.iterdir()}

    try:
        # 切换到隔离目录
        os.chdir(isolated_tmpdir)

        # 验证当前目录不是项目目录
        assert Path.cwd() != Path(original_cwd)
        assert ".git" not in orignal_files

        # 模拟GitInitRunner的行为但不实际运行它
        subprocess.run(["git", "init"], capture_output=True, check=True)

        # 验证git仓库只在隔离目录中创建
        assert (isolated_tmpdir / ".git").exists()
        assert ".git" not in orignal_files  # 项目目录应该仍然没有.git文件夹

    finally:
        # 清理隔离目录中的.git文件夹
        git_dir = isolated_tmpdir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        # 确保恢复原始工作目录
        os.chdir(original_cwd)
