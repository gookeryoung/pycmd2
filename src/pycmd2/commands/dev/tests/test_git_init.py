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
    """创建mock的cli对象, 确保在临时目录中运行.

    Yields:
        Generator[MagicMock, None, None]: mock的cli对象
    """
    with patch("pycmd2.commands.dev.gittools.git_init.get_client") as mock_get_client:
        mock_cli_instance = MagicMock()
        # 确保cwd指向隔离的临时目录而不是项目目录
        mock_cli_instance.cwd = str(tmp_path)
        mock_get_client.return_value = mock_cli_instance

        # 同时mock run_cmd方法
        mock_cli_instance.run_cmd = MagicMock()

        yield mock_cli_instance


@pytest.fixture
def isolated_tmpdir(tmp_path: Path) -> Generator[Path, None, None]:
    """创建一个完全隔离的临时目录用于git测试.

    Yields:
        Generator[Path, None, None]: 隔离的临时目录
    """
    git_test_dir = tmp_path / "git_test"
    git_test_dir.mkdir(exist_ok=True)
    original_cwd = Path.cwd()
    original_files = {f.name for f in original_cwd.iterdir() if f.is_dir()}

    try:
        yield git_test_dir
    finally:
        # 确保恢复原始工作目录
        os.chdir(original_cwd)

        # 验证项目目录没有被污染
        current_files = {f.name for f in original_cwd.iterdir() if f.is_dir()}
        if ".git" in current_files and ".git" not in original_files:
            # 如果意外创建了.git目录, 清理它
            git_dir = original_cwd / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)


def test_main_command_sequence(mock_cli: MagicMock, isolated_tmpdir: Path) -> None:
    """测试命令执行顺序, 确保在隔离的临时目录中运行."""
    # 在隔离目录中执行测试
    os.chdir(isolated_tmpdir)

    # 测试命令执行顺序
    runner = GitInitRunner()
    runner.run()

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
            # 现在应该调用两次chdir：一次切换到cli.cwd，一次恢复原始目录
            assert mock_chdir.call_count == 2  # noqa: PLR2004

            # 验证第一次切换到了mock cli的cwd目录
            first_call_args = mock_chdir.call_args_list[0][0]
            changed_dir = first_call_args[0]
            assert changed_dir == mock_cli.cwd

            # 验证第二次切换回了原始目录
            second_call_args = mock_chdir.call_args_list[1][0]
            restored_dir = second_call_args[0]
            assert str(restored_dir) == str(original_cwd)
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
    original_files = {f.name for f in original_cwd.iterdir()}

    try:
        # 切换到隔离目录
        os.chdir(isolated_tmpdir)

        # 验证当前目录不是项目目录
        assert Path.cwd() != Path(original_cwd)
        assert ".git" not in original_files

        # 模拟GitInitRunner的行为但不实际运行它
        result = subprocess.run(
            ["git", "init"],
            capture_output=True,
            text=True,
            check=True,
        )

        # 验证git init成功
        assert "Initialized empty Git repository" in result.stdout

        # 验证git仓库只在隔离目录中创建
        assert (isolated_tmpdir / ".git").exists()

        # 再次检查项目目录, 确保没有被污染
        current_files = {f.name for f in original_cwd.iterdir()}
        assert ".git" not in current_files  # 项目目录应该仍然没有.git文件夹

    finally:
        # 清理隔离目录中的.git文件夹
        git_dir = isolated_tmpdir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        # 确保恢复原始工作目录
        os.chdir(original_cwd)


def test_no_git_in_project_directory_after_test(isolated_tmpdir: Path) -> None:
    """测试执行后项目目录中不应该有.git文件夹."""
    original_cwd = Path.cwd()

    # 检查测试前的状态
    before_files = {f.name for f in original_cwd.iterdir()}

    try:
        # 在隔离目录中执行git操作
        os.chdir(isolated_tmpdir)
        subprocess.run(["git", "init"], capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            capture_output=True,
            check=True,
        )

        # 创建一个测试文件并提交
        test_file = isolated_tmpdir / "test.txt"
        test_file.write_text("test content")
        subprocess.run(["git", "add", "test.txt"], capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "test commit"],
            capture_output=True,
            check=True,
        )

        # 验证隔离目录中有完整的git仓库
        assert (isolated_tmpdir / ".git").exists()
        assert (isolated_tmpdir / "test.txt").exists()

    finally:
        # 清理隔离目录
        git_dir = isolated_tmpdir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)

        # 恢复工作目录
        os.chdir(original_cwd)

        # 验证项目目录没有被污染
        after_files = {f.name for f in original_cwd.iterdir()}
        assert ".git" not in after_files
        assert before_files == after_files  # 确保文件列表完全相同


def test_gitinit_runner_is_safe_with_real_cli(tmp_path: Path) -> None:
    """测试GitInitRunner在真实cli环境中也是安全的."""
    original_cwd = Path.cwd()
    git_test_dir = tmp_path / "safe_git_test"
    git_test_dir.mkdir(exist_ok=True)

    # 记录项目目录的初始状态
    project_git_dir = original_cwd / ".git"
    project_had_git_before = project_git_dir.exists()

    try:
        # 使用patch确保GitInitRunner使用临时目录
        with patch(
            "pycmd2.commands.dev.gittools.git_init.get_client",
        ) as mock_get_client:
            mock_cli = MagicMock()
            mock_cli.cwd = str(git_test_dir)
            mock_cli.run_cmd = MagicMock()  # Mock执行避免实际git操作
            mock_get_client.return_value = mock_cli

            # 执行GitInitRunner
            runner = GitInitRunner()
            runner.run()

            # 验证命令被正确调用
            assert mock_cli.run_cmd.call_count == 3  # noqa: PLR2004
            calls = mock_cli.run_cmd.call_args_list
            assert calls[0][0][0] == ["git", "init"]
            assert calls[1][0][0] == ["git", "add", "."]
            assert calls[2][0][0] == ["git", "commit", "-m", "initial commit"]

        # 验证项目目录状态没有被改变
        project_git_dir_after = original_cwd / ".git"
        project_has_git_after = project_git_dir_after.exists()

        # 如果项目之前没有git, 现在也不应该有
        if not project_had_git_before:
            assert not project_has_git_after, "项目目录不应该被初始化为git仓库"

        # 如果项目之前有git, 现在也应该还有（不应该被删除）
        if project_had_git_before:
            assert project_has_git_after, "项目目录的git仓库不应该被删除"

    finally:
        # 确保恢复工作目录
        os.chdir(original_cwd)

        # 清理测试目录
        test_git_dir = git_test_dir / ".git"
        if test_git_dir.exists():
            shutil.rmtree(test_git_dir)


def test_runner_restores_original_directory(tmp_path: Path) -> None:
    """测试运行器在执行后能正确恢复原始工作目录."""
    original_cwd = Path.cwd()
    git_test_dir = tmp_path / "restore_test"
    git_test_dir.mkdir(exist_ok=True)

    try:
        with patch(
            "pycmd2.commands.dev.gittools.git_init.get_client",
        ) as mock_get_client:
            mock_cli = MagicMock()
            mock_cli.cwd = str(git_test_dir)
            mock_cli.run_cmd = MagicMock()
            mock_get_client.return_value = mock_cli

            # 记录执行前的工作目录
            cwd_before = Path.cwd()
            assert cwd_before == original_cwd

            # 执行GitInitRunner
            runner = GitInitRunner()
            runner.run()

            # 验证执行后工作目录被恢复
            cwd_after = Path.cwd()
            assert cwd_after == original_cwd

            # 验证命令被执行
            assert mock_cli.run_cmd.call_count == 3  # noqa: PLR2004

    finally:
        # 确保在测试失败时也能恢复工作目录
        os.chdir(original_cwd)
