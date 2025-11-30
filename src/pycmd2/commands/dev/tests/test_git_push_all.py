import os
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from pycmd2.commands.dev.gittools.git_push_all import _check_sensitive_data
from pycmd2.commands.dev.gittools.git_push_all import _get_cmd_full_path
from pycmd2.commands.dev.gittools.git_push_all import check_git_status
from pycmd2.commands.dev.gittools.git_push_all import CommandNotFoundError
from pycmd2.commands.dev.gittools.git_push_all import git_push_all
from pycmd2.commands.dev.gittools.git_push_all import GitPushAllRunner


@pytest.fixture
def mock_cli() -> Generator[MagicMock, None, None]:
    """创建mock的cli对象.

    Yields:
        None
    """
    with patch(
        "pycmd2.commands.dev.gittools.git_push_all.get_client",
    ) as mock_get_client:
        mock_cli_instance = MagicMock()
        mock_get_client.return_value = mock_cli_instance
        yield mock_cli_instance


@pytest.fixture
def mock_subprocess_run() -> Generator[Mock, None, None]:
    """创建mock的subprocess.run对象.

    Yields:
        None
    """
    with patch("pycmd2.commands.dev.gittools.git_push_all.subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def mock_shutil_which() -> Generator[Mock, None, None]:
    """创建mock的shutil.which对象.

    Yields:
        None.
    """
    with patch("pycmd2.commands.dev.gittools.git_push_all.shutil.which") as mock_which:
        yield mock_which


def test_get_cmd_full_path_success(mock_shutil_which: Mock) -> None:
    """测试成功获取命令路径."""
    mock_shutil_which.return_value = "/usr/bin/git"
    assert _get_cmd_full_path("git") == "/usr/bin/git"


def test_get_cmd_full_path_failure(mock_shutil_which: Mock) -> None:
    """测试命令不存在时抛出异常."""
    mock_shutil_which.return_value = None
    with pytest.raises(CommandNotFoundError, match="命令不存在: nonexistent"):
        _get_cmd_full_path("nonexistent")


def test_check_git_status_clean(
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试git状态检查 - 干净状态."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = ""
    assert check_git_status() is True


def test_check_git_status_dirty(
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试git状态检查 - 有未提交修改."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = " M file.txt"
    assert check_git_status() is False


def test_check_sensitive_data_clean(
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试敏感数据检查 - 无敏感文件."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = "file.txt"
    assert _check_sensitive_data() is True


def test_check_sensitive_data_dirty(
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试敏感数据检查 - 存在敏感文件."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = ".env"
    assert _check_sensitive_data() is False


def test_push_success(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试推送成功的情况."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = ""

    git_push_all("origin")

    # 验证执行了所有推送命令
    assert mock_cli.run_cmd.call_count == 3  # noqa: PLR2004
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "origin"])


def test_push_with_dirty_status(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试存在未提交修改时不推送."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = " M file.txt"

    git_push_all("origin")

    # 验证没有执行任何推送命令
    assert mock_cli.run_cmd.call_count == 0


def test_push_with_sensitive_data(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试存在敏感数据时不推送."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.side_effect = [
        MagicMock(stdout=""),  # check_git_status
        MagicMock(stdout=".env"),  # check_sensitive_data
    ]

    git_push_all("origin")

    # 验证没有执行任何推送命令
    assert mock_cli.run_cmd.call_count == 0


def test_push_with_both_issues(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试同时存在未提交修改和敏感数据时不推送."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = " M file.txt"  # 模拟有未提交修改

    git_push_all("origin")

    # 验证没有执行任何推送命令
    assert mock_cli.run_cmd.call_count == 0


def test_get_cmd_full_path_custom_command(mock_shutil_which: Mock) -> None:
    """测试获取自定义命令路径."""
    mock_shutil_which.return_value = "/usr/local/bin/custom-cmd"
    assert _get_cmd_full_path("custom-cmd") == "/usr/local/bin/custom-cmd"


def test_git_push_all_runner_success(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试GitPushAllRunner成功执行."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = ""

    runner = GitPushAllRunner()
    runner.run()

    # 验证调用了所有远程仓库的推送
    assert mock_cli.run_cmd.call_count == 9  # noqa: PLR2004

    # 验证调用了origin
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "origin"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "origin"])

    # 验证调用了gitee.com
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "gitee.com"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "gitee.com"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "gitee.com"])

    # 验证调用了github.com
    mock_cli.run_cmd.assert_any_call(["git", "fetch", "github.com"])
    mock_cli.run_cmd.assert_any_call(["git", "pull", "--rebase", "github.com"])
    mock_cli.run_cmd.assert_any_call(["git", "push", "--all", "github.com"])


def test_git_push_all_runner_with_dirty_status(
    mock_cli: MagicMock,
    mock_subprocess_run: Mock,
    mock_shutil_which: Mock,
) -> None:
    """测试GitPushAllRunner在有未提交修改时不执行推送."""
    mock_shutil_which.return_value = "/usr/bin/git"
    mock_subprocess_run.return_value.stdout = " M file.txt"

    runner = GitPushAllRunner()
    runner.run()

    # 验证没有执行任何推送命令
    assert mock_cli.run_cmd.call_count == 0


def test_git_push_all_runner_isolation(tmp_path: Path) -> None:
    """测试GitPushAllRunner的隔离性确保不会污染项目目录."""
    original_cwd = Path.cwd()
    project_files_before = {f.name for f in original_cwd.iterdir()}

    try:
        with patch(
            "pycmd2.commands.dev.gittools.git_push_all.get_client",
        ) as mock_get_client:
            mock_cli = MagicMock()
            mock_cli.cwd = str(tmp_path)
            mock_get_client.return_value = mock_cli

            with patch(
                "pycmd2.commands.dev.gittools.git_push_all.subprocess.run",
            ) as mock_run:
                mock_run.return_value.stdout = ""

                runner = GitPushAllRunner()
                runner.run()

                # 验证工作目录没有被改变
                assert Path.cwd() == original_cwd

                # 验证命令被执行
                assert mock_cli.run_cmd.call_count == 9  # noqa: PLR2004

        # 验证项目目录没有被污染
        project_files_after = {f.name for f in original_cwd.iterdir()}
        assert project_files_before == project_files_after

    finally:
        # 确保恢复工作目录
        if Path.cwd() != original_cwd:
            os.chdir(original_cwd)
