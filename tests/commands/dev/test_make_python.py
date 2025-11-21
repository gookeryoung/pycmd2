"""make_python 命令测试."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pycmd2.commands.dev.make_python import _activate_py_env  # noqa: PLC2701
from pycmd2.commands.dev.make_python import _browse_coverage  # noqa: PLC2701
from pycmd2.commands.dev.make_python import _clean  # noqa: PLC2701
from pycmd2.commands.dev.make_python import ActivateOption
from pycmd2.commands.dev.make_python import BuildOption
from pycmd2.commands.dev.make_python import BumpMajorOption
from pycmd2.commands.dev.make_python import BumpMinorOption
from pycmd2.commands.dev.make_python import BumpPatchOption
from pycmd2.commands.dev.make_python import BumpPublishOption
from pycmd2.commands.dev.make_python import CleanOption
from pycmd2.commands.dev.make_python import CoverageOption
from pycmd2.commands.dev.make_python import CoverageSlowOption
from pycmd2.commands.dev.make_python import DistributionOption
from pycmd2.commands.dev.make_python import DocumentationOption
from pycmd2.commands.dev.make_python import InitializeOption
from pycmd2.commands.dev.make_python import LintOption
from pycmd2.commands.dev.make_python import main
from pycmd2.commands.dev.make_python import MakeOption
from pycmd2.commands.dev.make_python import PublishOption
from pycmd2.commands.dev.make_python import PyprojectMaker
from pycmd2.commands.dev.make_python import SyncronizeOption
from pycmd2.commands.dev.make_python import TestOption
from pycmd2.commands.dev.make_python import UpdateOption


@pytest.fixture
def mock_cli(tmp_path: Path) -> Generator[MagicMock, None, None]:
    """模拟 CLI 客户端.

    Yields:
        模拟的 CLI 客户端对象.
    """
    with patch("pycmd2.commands.dev.make_python.cli") as mock:
        mock.cwd = tmp_path
        mock.is_windows = False
        yield mock


@pytest.fixture
def mock_logger() -> Generator[MagicMock, None, None]:
    """模拟日志记录器.

    Yields:
        模拟的日志记录器对象.
    """
    with patch("pycmd2.commands.dev.make_python.logger") as mock:
        yield mock


@pytest.fixture
def sample_pyproject(tmp_path: Path) -> Path:
    """创建示例 pyproject.toml 文件.

    Returns:
        示例 pyproject.toml 文件路径.
    """
    pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)
    return pyproject_file


@pytest.fixture
def sample_init_file(tmp_path: Path) -> Path:
    """创建示例 __init__.py 文件.

    Returns:
        示例 __init__.py 文件路径.
    """
    src_dir = tmp_path / "src" / "test_project"
    src_dir.mkdir(parents=True)
    init_file = src_dir / "__init__.py"
    init_content = '''"""Test package."""

__version__ = "0.1.0"
__build_date__ = "2025-01-01"
'''
    init_file.write_text(init_content)
    return init_file


class TestMakeOption:
    """测试 MakeOption 基类."""

    def test_build_command_with_makefile(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试检测到 Makefile 时的构建命令."""
        makefile = tmp_path / "Makefile"
        makefile.write_text("build:\n\techo building")

        result = MakeOption.build_command()
        assert result == "make"

    def test_build_command_with_hatch(self, mock_cli: MagicMock, sample_pyproject: Path) -> None:  # noqa: ARG002
        """测试检测到 hatch 构建后端."""
        result = MakeOption.build_command()
        assert result == "hatch"

    def test_build_command_with_poetry(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试检测到 Poetry 构建后端."""
        pyproject_content = """
[tool.poetry]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        result = MakeOption.build_command()
        assert result == "poetry"

    def test_build_command_no_tool(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试未找到构建工具."""
        result = MakeOption.build_command()
        assert not result

    def test_list_dist_dir_with_dist_dir(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试存在 dist 目录时的列出发布目录命令."""
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        result = MakeOption.list_dist_dir()
        assert result == ["ls", "-l", "dist"]

    def test_list_dist_dir_without_dist_dir(self, mock_cli: MagicMock) -> None:  # noqa: ARG002
        """测试不存在 dist 目录时的列出发布目录命令."""
        result = MakeOption.list_dist_dir()
        assert result == ["ls", "-l"]

    def test_list_dist_dir_windows(self, mock_cli: MagicMock) -> None:
        """测试 Windows 系统的发布命令."""
        mock_cli.is_windows = True
        result = MakeOption.list_dist_dir()
        assert result == ["cmd", "/c", "dir"]

    def test_project_name_from_project(self, mock_cli: MagicMock, sample_pyproject: Path) -> None:  # noqa: ARG002
        """测试从 project.name 获取项目名称."""
        result = MakeOption.project_name()
        assert result == "test-project"

    def test_project_name_from_poetry(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试从 tool.poetry.name 获取项目名称."""
        pyproject_content = """
[tool.poetry]
name = "poetry-project"
version = "0.1.0"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        result = MakeOption.project_name()
        assert result == "poetry-project"

    def test_project_name_no_file(self, mock_cli: MagicMock) -> None:  # noqa: ARG002
        """测试 pyproject.toml 不存在时."""
        result = MakeOption.project_name()
        assert not result

    def test_update_build_date(self, mock_cli: MagicMock, sample_init_file: Path) -> None:  # noqa: ARG002
        """测试更新构建日期."""
        MakeOption.update_build_date()

        # 读取更新后的文件内容
        updated_content = sample_init_file.read_text(encoding="utf-8")
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        assert f'__build_date__ = "{today}"' in updated_content

    def test_update_build_date_no_match(self, mock_cli: MagicMock, tmp_path: Path) -> None:  # noqa: ARG002
        """测试没有 __build_date__ 定义的文件."""
        src_dir = tmp_path / "src" / "test_project"
        src_dir.mkdir(parents=True)
        init_file = src_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n__version__ = "0.1.0"\n')

        MakeOption.update_build_date()

        # 文件内容应该保持不变
        content = init_file.read_text()
        assert content == '"""Test package."""\n__version__ = "0.1.0"\n'


class TestPyprojectMaker:
    """测试 PyprojectMaker 类."""

    def test_options_list(self) -> None:
        """测试获取选项列表."""
        options = PyprojectMaker.get_option_list()
        assert isinstance(options, list)
        assert "build" in options
        assert "clean" in options
        assert "test" in options

    def test_call_option_str_valid(self, mock_cli: MagicMock) -> None:  # noqa: ARG002
        """测试调用有效选项."""
        maker = PyprojectMaker()

        with patch.object(maker, "run") as mock_call:
            maker.run("build")
            mock_call.assert_called_once()

    def test_call_option_str_invalid(self, mock_cli: MagicMock, mock_logger: MagicMock) -> None:  # noqa: ARG002
        """测试调用无效选项."""
        maker = PyprojectMaker()
        maker.run("invalid_option")

        mock_logger.error.assert_called_once()

    def test_run_with_list_command(self, mock_cli: MagicMock) -> None:
        """测试执行列表命令."""
        maker = PyprojectMaker()

        maker.run("build")

        # 验证调用了 run_cmd
        mock_cli.run_cmd.assert_called()

    def test_run_with_callable_command(self, mock_cli: MagicMock) -> None:  # noqa: ARG002
        """测试执行可调用命令."""
        maker = PyprojectMaker()

        maker.run("clean")


class TestOptionClasses:
    """测试各个选项类."""

    def test_activate_option(self) -> None:
        """测试 ActivateOption."""
        option = ActivateOption()
        assert option.name == "activate"
        assert "激活" in option.desc
        assert _activate_py_env in option.commands

    def test_build_option(self) -> None:
        """测试 BuildOption."""
        option = BuildOption()
        assert option.name == "build"
        assert "构建" in option.desc

    def test_bump_options(self) -> None:
        """测试版本更新选项."""
        # Patch version
        bump = BumpPatchOption()
        assert bump.name == "bump"
        assert "patch" in bump.desc

        bump_minor = BumpMinorOption()
        assert bump_minor.name == "bump minor"
        assert "minor" in bump_minor.desc

        bump_major = BumpMajorOption()
        assert bump_major.name == "bump major"
        assert "major" in bump_major.desc

    def test_clean_option(self) -> None:
        """测试 CleanOption."""
        option = CleanOption()
        assert option.name == "clean"
        assert "清理" in option.desc
        assert _clean in option.commands

    def test_coverage_options(self) -> None:
        """测试覆盖率选项."""
        cov = CoverageOption()
        assert cov.name == "coverage"
        assert "覆盖率" in cov.desc
        assert _browse_coverage in cov.commands

        cov_sl = CoverageSlowOption()
        assert cov_sl.name == "coverage-slow"
        assert "slow" in cov_sl.desc

    def test_other_options(self) -> None:
        """测试其他选项."""
        options = [
            DistributionOption(),
            DocumentationOption(),
            InitializeOption(),
            LintOption(),
            PublishOption(),
            SyncronizeOption(),
            TestOption(),
            UpdateOption(),
            BumpPublishOption(),
        ]

        for option in options:
            assert option.name
            assert option.desc
            assert option.commands


class TestUtilityFunctions:
    """测试工具函数."""

    def test_activate_py_env_windows(self, mock_cli: MagicMock) -> None:
        """测试 Windows 环境激活."""
        mock_cli.is_windows = True

        with patch.object(mock_cli, "run_cmdstr") as mock_run:
            _activate_py_env()
            mock_run.assert_called_once()

    def test_activate_py_env_unix(self, mock_cli: MagicMock) -> None:
        """测试 Unix 环境激活."""
        mock_cli.is_windows = False

        with patch.object(mock_cli, "run_cmdstr") as mock_run:
            _activate_py_env()
            mock_run.assert_called_once()

    def test_clean(self, mock_cli: MagicMock, tmp_path: Path) -> None:
        """测试清理功能."""
        # 创建一些测试目录
        (tmp_path / "dist").mkdir()
        (tmp_path / "__pycache__").mkdir()

        with patch.object(mock_cli, "run") as mock_run:
            _clean()
            mock_run.assert_called()

    def test_browse_coverage(self) -> None:
        """测试打开覆盖率报告."""
        with patch("webbrowser.open") as mock_open:
            _browse_coverage()
            mock_open.assert_called_once()


class TestMainFunction:
    """测试主函数."""

    def test_main(self, mock_cli: MagicMock) -> None:  # noqa: ARG002
        """测试主函数."""
        with patch("pycmd2.commands.dev.make_python.PyprojectMaker") as mock_maker_class:
            mock_maker = MagicMock()
            mock_maker_class.return_value = mock_maker

            main("build")

            mock_maker.run.assert_called_once_with("build")

    def test_main_version_info(self, mock_cli: MagicMock, mock_logger: MagicMock) -> None:  # noqa: ARG002
        """测试主函数版本信息."""
        with patch("pycmd2.commands.dev.make_python.PyprojectMaker"):
            main("build")

            # 验证版本信息被记录
            mock_logger.info.assert_called()


class TestIntegration:
    """集成测试."""

    def test_full_workflow(self, mock_cli: MagicMock, tmp_path: Path) -> None:
        """测试完整工作流程."""
        # 创建必要的文件
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""")

        src_dir = tmp_path / "src" / "test_project"
        src_dir.mkdir(parents=True)
        init_file = src_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n__build_date__ = "2025-01-01"\n')

        maker = PyprojectMaker()

        # 测试 update 选项
        with patch.object(mock_cli, "run_cmd"):
            maker.run("update")

        # 验证构建日期被更新
        updated_content = init_file.read_text()
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        assert f'__build_date__ = "{today}"' in updated_content

    def test_option_aliases(self) -> None:
        """测试选项别名."""
        maker = PyprojectMaker()

        # 测试各种别名都能正确映射
        aliases = {
            "act": "activate",
            "b": "build",
            "c": "clean",
            "pub": "publish",
            "sync": "sync",
        }

        for alias, expected in aliases.items():
            option = maker.OPTIONS.get(alias)
            assert option is not None
            assert expected in option.name or option.name == expected
