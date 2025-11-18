"""功能: python 项目用构建命令.

命令: mkp [OPTIONS]
"""

from __future__ import annotations

import datetime
import logging
import re
import shutil
import webbrowser
from functools import partial
from pathlib import Path
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import List
from urllib.request import pathname2url

import typer

from pycmd2.client import get_client
from pycmd2.commands.dev.git_push_all import main as git_push_all

try:
    import tomllib  # type: ignore[import]
except ModuleNotFoundError:
    import tomli as tomllib


__version__ = "0.1.2"
__build_date__ = "2025-08-02"

cli = get_client()
logger = logging.getLogger(__name__)


class MakeOption:
    """MakeOption 选项."""

    name: str
    commands: list[str | list[str] | Callable[..., Any]]
    desc: str = ""

    @classmethod
    def src_dir(cls) -> Path:
        """获取源代码目录.

        Returns:
            Path: 源代码目录
        """
        return cli.cwd / "src"

    @classmethod
    def build_command(cls) -> str:
        """获取构建命令.

        Returns:
            str: 构建命令
        """
        makefile = Path.cwd() / "Makefile"

        if makefile.exists():
            return "make"

        pyproject_file = Path.cwd() / "pyproject.toml"
        if pyproject_file.exists():
            logger.info("检测到 pyproject.toml 文件")
            with pyproject_file.open("rb") as f:
                conf = tomllib.load(f)
                if all(
                    [
                        "build-system" in conf,
                        "build-backend" in conf["build-system"],
                        "hatch" in conf["build-system"]["build-backend"],
                    ],
                ):
                    return "hatch"

        logger.error("未找到构建工具, 请手动构建")
        return ""

    @classmethod
    def dist_command(cls) -> List[str]:
        """获取发布命令.

        Returns:
            str: 发布命令
        """
        return ["ls", "-l", "dist"] if (Path.cwd() / "dist").exists() else ["ls", "-l"]

    @classmethod
    def project_name(cls) -> str:
        """获取项目目录.

        Returns:
            str: 项目目录
        """
        cfg_file = cli.cwd / "pyproject.toml"
        if not cfg_file.exists():
            logger.error(
                f"pyproject.toml 文件不存在, 无法获取项目目录: [red]{cfg_file}",
            )
            return ""

        # 如果 pyproject.toml 存在, 尝试从中获取项目名称
        try:
            with cfg_file.open("rb") as f:
                config = tomllib.load(f)
                project_name = config["project"]["name"] or config["tool"]["poetry"]["name"]

                return project_name or ""
        except Exception as e:
            msg = f"读取 pyproject.toml 失败: {e.__class__.__name__}: {e}"
            logger.exception(msg)
            return ""

    @classmethod
    def update_build_date(cls) -> None:
        """更新构建日期."""
        build_date = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d",
        )
        init_files = cls.src_dir().rglob("__init__.py")

        for init_file in init_files:
            try:
                with init_file.open("r+", encoding="utf-8") as f:
                    content = f.read()

                    # 使用正则表达式匹配各种格式的日期声明
                    pattern = re.compile(
                        r"^(\s*)"  # 缩进
                        r"(__build_date__)\s*=\s*"  # 变量名
                        r"([\"\']?)"  # 引号类型(第3组)
                        r"(\d{4}-\d{2}-\d{2})"  # 原日期(第4组)
                        r"\3"  # 闭合引号
                        r"(\s*(#.*)?)$",  # 尾部空格和注释(第5组)
                        flags=re.MULTILINE | re.IGNORECASE,
                    )

                    # 查找所有匹配项
                    matches = pattern.findall(content)
                    match = pattern.search(content)
                    if not matches or not match:
                        logger.warning("未找到 __build_date__ 定义")
                        return

                    # 构造新行(保留原始格式).
                    quote = match.group(3) or ""  # 获取原引号(可能为空)
                    new_line = f"{match.group(1)}{match.group(2)} = {quote}{build_date}{quote}{match.group(5)}"
                    new_content = pattern.sub(new_line, content, count=1)

                    # 检查是否需要更新
                    if new_content == content:
                        logger.info("构建日期已是最新, 无需更新")

                    # 回写文件
                    f.seek(0)
                    f.write(new_content)
                    f.truncate()
            except Exception as e:
                msg = f"操作失败: [red]{init_file}, {e.__class__.__name__}: {e}"
                logger.exception(msg)
                return

            logger.info(
                f"更新文件: {init_file}, __build_date__ -> {build_date}",
            )


def _activate_py_env() -> None:
    extension = ".bat" if cli.is_windows else ""
    actviate_path = cli.cwd / ".venv" / "Scripts" / f"activate{extension}"
    cli.run_cmdstr(str(actviate_path))


class ActivateOption(MakeOption):
    """激活项目环境."""

    name = "activate"
    desc = "激活项目环境, 别名: act / activate"
    commands: ClassVar = [_activate_py_env]


class BuildOption(MakeOption):
    """构建项目."""

    name = "build"
    desc = "构建项目"
    commands: ClassVar = [[MakeOption.build_command(), "build"]]


class BumpPublishOption(MakeOption):
    """执行版本更新、构建以及推送等系列操作."""

    name = "bump and publish"
    desc = "执行版本更新、构建以及推送等系列操作"
    commands: ClassVar = ["bump", "pub"]


class BumpOption(MakeOption):
    """更新 patch 版本."""

    name = "bump"
    desc = "更新 patch 版本"
    commands: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "patch"],
    ]


class BumpMinorOption(MakeOption):
    """更新 minor 版本."""

    name = "bump minor"
    desc = "更新 minor 版本"
    commands: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "minor"],
    ]


class BumpMajorOption(MakeOption):
    """更新 major 版本."""

    name = "bump major"
    desc = "更新 major 版本"
    commands: ClassVar = [
        "update",
        ["uvx", "--from", "bump2version", "bumpversion", "major"],
    ]


def _clean() -> None:
    """清理项目."""
    # 待清理目录
    dirs = [
        "dist",
        ".tox",
        ".coverage",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
    ]
    spec_dirs = [cli.cwd / d for d in dirs]
    cache_dirs = list(cli.cwd.rglob("**/__pycache__"))
    remove_func = partial(shutil.rmtree, ignore_errors=True)

    # 移除待清理目录
    if spec_dirs:
        cli.run(remove_func, spec_dirs)
    if cache_dirs:
        cli.run(remove_func, cache_dirs)


class CleanOption(MakeOption):
    """清理项目."""

    name = "clean"
    desc = "清理所有构建、测试生成的临时内容, 别名: c / clean"
    commands: ClassVar = [_clean]


def _browse_coverage() -> None:
    """打开浏览器查看测试覆盖率结果."""
    webbrowser.open(
        "file://" + pathname2url(str(cli.cwd / "htmlcov" / "index.html")),
    )


class CoverageOption(MakeOption):
    """测试覆盖率检查."""

    name = "coverage"
    desc = "测试覆盖率检查"
    commands: ClassVar = [
        "sync",
        [
            "pytest",
            "--cov",
        ],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


class CoverageSlowOption(CoverageOption):
    """测试覆盖率检查, 包含slow测试项目."""

    name = "coverage-slow"
    desc = "测试覆盖率检查, 包含slow测试项目"
    commands: ClassVar = [
        "sync",
        [
            "pytest",
            "--cov",
            "--runslow",
        ],
        ["coverage", "report", "-m"],
        ["coverage", "html"],
        _browse_coverage,
    ]


class DistributionOption(MakeOption):
    """生成分发包."""

    name = "distribution"
    desc = "生成分发包"
    commands: ClassVar = [
        "clean",
        "sync",
        [MakeOption.build_command(), "build"],
        MakeOption.dist_command(),
    ]


class DocumentationOption(MakeOption):
    """生成 Sphinx HTML 文档, 包括 API."""

    name = "documentation"
    desc = "生成 Sphinx HTML 文档, 包括 API"
    commands: ClassVar = [
        ["rm", "-f", "./docs/modules.rst"],
        ["rm", "-f", f"./docs/{MakeOption.project_name()}*.rst"],
        ["rm", "-rf", "./docs/_build"],
        ["sphinx-apidoc", "-o", "docs", f"src/{MakeOption.project_name()}"],
        ["sphinx-build", "docs", "docs/_build"],
        [
            "sphinx-autobuild",
            "docs",
            "docs/_build/html",
            "--watch",
            ".",
            "--open-browser",
        ],
    ]


class InitializeOption(MakeOption):
    """项目初始化."""

    name = "initialize"
    desc = "项目初始化"
    commands: ClassVar = [
        "clean",
        "sync",
        ["git", "init"],
        ["uvx", "pre-commit", "install"],
    ]


class LintOption(MakeOption):
    """代码质量检查."""

    name = "lint"
    desc = "代码质量检查"
    commands: ClassVar = [
        "sync",
        ["uvx", "ruff", "check", "src", "tests", "--fix"],
    ]


class PublishOption(MakeOption):
    """执行构建以及推送等系列操作."""

    name = "publish"
    desc = "执行构建以及推送等系列操作, 别名: pub / publish"
    commands: ClassVar = [
        "dist",
        [MakeOption.build_command(), "publish"],
        ["gitc", "-f"],
        git_push_all,
    ]


class SyncronizeOption(MakeOption):
    """同步项目环境."""

    name = "sync"
    desc = "同步项目环境, 别名: sync"
    commands: ClassVar = [
        ["uv", "sync"],
        ["uvx", "pre-commit", "install"],
    ]


class TestOption(MakeOption):
    """测试."""

    name = "test"
    desc = "运行测试"
    commands: ClassVar = [
        "sync",
        ["pytest"],
    ]


class UpdateOption(MakeOption):
    """更新构建日期."""

    name = "update"
    desc = "更新构建日期"
    commands: ClassVar = [
        MakeOption.update_build_date,
        ["git", "add", "*/**/__init__.py"],
        ["git", "commit", "-m", "更新构建日期"],
    ]


class PyprojectMaker:
    """Python 项目构建器.

    options: Dict[str, MakeOption]
        可用的构建选项字典, 键为选项名称, 值为 MakeOption 子类实例
    call_option_str(option_name: str) -> None
        调用指定的构建选项
    options_list() -> List[str]
        获取所有可用的选项名称列表
    _call_option(option: MakeOption) -> None
        内部调用选项, 执行其命令并处理描述信息
    """

    options: ClassVar[dict[str, MakeOption]] = {
        "act": ActivateOption(),
        "build": BuildOption(),
        "bpub": BumpPublishOption(),
        "bump": BumpOption(),
        "bumpi": BumpMinorOption(),
        "bumpa": BumpMajorOption(),
        "c": CleanOption(),
        "clean": CleanOption(),
        "cov": CoverageOption(),
        "covsl": CoverageSlowOption(),
        "dist": DistributionOption(),
        "doc": DocumentationOption(),
        "init": InitializeOption(),
        "lint": LintOption(),
        "pub": PublishOption(),
        "publish": PublishOption(),
        "sync": SyncronizeOption(),
        "test": TestOption(),
        "update": UpdateOption(),
    }

    def call_option_str(self, option_name: str) -> None:
        """调用指定的构建选项."""
        option = self.options.get(option_name, None)
        if not option:
            logger.error(
                f"未找到匹配选项: {option_name}, 选项列表: [red]{self.options_list()}",
            )
            return

        self._call_option(option)

    @classmethod
    def options_list(cls) -> list[str]:
        """获取所有可用的选项名称列表.

        Returns:
            list[str]: 可用选项名称列表
        """
        return list(cls.options.keys())

    def _call_option(self, option: MakeOption) -> None:
        """内部调用选项."""
        logger.info(f"调用选项: mkp [green bold]{option.name}")
        if option.desc:
            logger.info(f"功能描述: [purple bold]{option.desc}")

        for command in option.commands:
            if isinstance(command, str):
                child_opt = self.options.get(command, None)
                if child_opt:
                    logger.info(f"执行子命令: [purple]{child_opt.name}")
                    self._call_option(child_opt)
                else:
                    logger.error(f"未找到匹配选项: {command}")
                    return
            elif isinstance(command, list):
                cli.run_cmd(command)
            elif callable(command):
                command()
            else:
                logger.error(f"未知命令类型: {type(command)}, 内容: {command}")


@cli.app.command()
def main(
    optstr: str = typer.Argument(
        help=f"构建选项: {PyprojectMaker.options_list()}",
    ),
) -> None:
    logger.info(f"mkp {__version__}, 构建日期: {__build_date__}")

    pm = PyprojectMaker()
    pm.call_option_str(optstr)
