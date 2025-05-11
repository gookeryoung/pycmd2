"""功能：python 项目用构建命令"""

import datetime
import logging
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Union

from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.git.git_push_all import main as git_push_all

cli = get_client()

SRC_DIR = cli.CWD / "src"
PROJECTS_DIRS = list(f for f in SRC_DIR.iterdir())

if not len(PROJECTS_DIRS):
    logging.error(
        f"当前目录下不存在 python 项目: {cli.CWD}, 结构: ./src/project-name"
    )
    sys.exit(1)

PROJECT_DIR = PROJECTS_DIRS[0]
PROJECT_NAME = PROJECT_DIR.stem

if not PROJECT_DIR.exists():
    logging.error(
        f"当前目录下不存在 python 项目: {cli.CWD}, 结构: ./src/project-name"
    )
    sys.exit(1)


@dataclass
class MakeOption:
    name: str
    commands: List[Union[str, List[str], Callable[..., Any]]]
    desc: str = ""


def _update_build_date():
    build_date = datetime.datetime.now().strftime("%Y-%m-%d")
    src_dir = cli.CWD / "src"
    init_files = src_dir.rglob("__init__.py")

    for init_file in init_files:
        try:
            with init_file.open("r+", encoding="utf-8") as f:
                content = f.read()

                # 使用正则表达式匹配各种格式的日期声明
                pattern = re.compile(
                    r"^(\s*)"  # 缩进
                    r"(__build_date__)\s*=\s*"  # 变量名
                    r'(["\']?)'  # 引号类型（第3组）
                    r"(\d{4}-\d{2}-\d{2})"  # 原日期（第4组）
                    r"\3"  # 闭合引号
                    r"(\s*(#.*)?)$",  # 尾部空格和注释（第5组）
                    flags=re.MULTILINE | re.IGNORECASE,
                )

                # 查找所有匹配项
                matches = pattern.findall(content)
                if not matches:
                    logging.warning("未找到 __build_date__ 定义")
                    return False

                match = pattern.search(content)
                if not match:
                    logging.warning("未找到有效的 __build_date__ 定义")
                    return False

                # 构造新行（保留原始格式）
                quote = match.group(3) or ""  # 获取原引号（可能为空）
                new_line = f"{match.group(1)}{match.group(2)} = {quote}{build_date}{quote}{match.group(5)}"  # noqa
                new_content = pattern.sub(new_line, content, count=1)

                # 检查是否需要更新
                if new_content == content:
                    logging.info("构建日期已是最新，无需更新")
                    return True

                # 回写文件
                f.seek(0)
                f.write(new_content)
                f.truncate()
        except Exception as e:
            logging.error(f"操作失败: [red]{init_file}, {str(e)}")
            return False

        logging.info(f"更新文件: {init_file}, __build_date__ -> {build_date}")
        return True


def _browse_coverage() -> None:
    """打开浏览器查看测试覆盖率结果"""

    import webbrowser
    from urllib.request import pathname2url

    webbrowser.open(
        "file://" + pathname2url(str(cli.CWD / "htmlcov" / "index.html"))
    )


def _clean() -> None:
    """清理项目"""

    # 待清理目录
    dirs = [
        "dist",
        ".tox",
        ".coverage",
        "htmlcov",
        ".pytest_cache",
        ".mypy_cache",
    ]
    spec_dirs = [cli.CWD / d for d in dirs]

    # 定义移除函数
    def remove_dir(dirpath: Path) -> None:
        shutil.rmtree(dirpath, ignore_errors=True)

    # 移除待清理目录
    cli.run(remove_dir, spec_dirs)

    # 移除临时目录
    cache_dirs = list(d for d in cli.CWD.rglob("__pycache__") if d.is_dir())
    cli.run(remove_dir, cache_dirs)


MAKE_OPTIONS: Dict[str, MakeOption] = dict(
    bump=MakeOption(
        name="bump",
        desc="更新 patch 版本",
        commands=[
            ["uvx", "--from", "bump2version", "bumpversion", "patch"],
            _update_build_date,
            ["git", "add", "*/**/__init__.py"],
        ],
    ),
    bumpi=MakeOption(
        name="bump",
        desc="更新 minor 版本",
        commands=[
            ["uvx", "--from", "bump2version", "bumpversion", "minor"],
            _update_build_date,
            ["git", "add", "*/**/__init__.py"],
        ],
    ),
    bumpa=MakeOption(
        name="bump",
        desc="更新 major 版本",
        commands=[
            ["uvx", "--from", "bump2version", "bumpversion", "major"],
            _update_build_date,
            ["git", "add", "*/**/__init__.py"],
        ],
    ),
    c=MakeOption(
        name="clean",
        commands=["clean"],
    ),
    clean=MakeOption(
        name="clean",
        desc="清理所有构建、测试生成的临时内容",
        commands=[_clean],
    ),
    cov=MakeOption(
        name="coverage",
        desc="测试覆盖率检查",
        commands=[
            "sync",
            ["coverage", "run", "--source", PROJECT_NAME, "-m", "pytest"],
            ["coverage", "report", "-m"],
            ["coverage", "html"],
            _browse_coverage,
        ],
    ),
    dist=MakeOption(
        name="dist",
        desc="使用 hatch 构建 whl 包",
        commands=[
            "clean",
            ["hatch", "build"],
            ["ls", "-l", "dist"],
        ],
    ),
    doc=MakeOption(
        name="document",
        desc="生成 Sphinx HTML 文档, 包括 API",
        commands=[
            ["rm", "-f", "./docs/modules.rst"],
            ["rm", "-f", f"./docs/{PROJECT_NAME}*.rst"],
            ["rm", "-rf", "./docs/_build"],
            ["sphinx-apidoc", "-o", "docs", f"src/{PROJECT_NAME}"],
            ["sphinx-build", "docs", "docs/_build"],
            [
                "sphinx-autobuild",
                "docs",
                "docs/_build/html",
                "--watch",
                ".",
                "--open-browser",
            ],
        ],
    ),
    init=MakeOption(
        name="initialize",
        desc="项目初始化",
        commands=[
            "clean",
            "sync",
            ["git", "init"],
            ["uvx", "pre-commit", "install"],
        ],
    ),
    lint=MakeOption(
        name="lint",
        desc="代码质量检查",
        commands=[
            "sync",
            ["ruff", "check", "src", "tests", "--fix"],
        ],
    ),
    pub=MakeOption(
        name="publish",
        desc="执行版本更新、构建以及推送等系列操作",
        commands=[
            "bump",
            "dist",
            ["hatch", "publish"],
            git_push_all,
        ],
    ),
    sync=MakeOption(
        name="sync",
        desc="项目环境同步",
        commands=[
            ["uv", "sync"],
        ],
    ),
    test=MakeOption(
        name="test",
        desc="运行测试",
        commands=[
            "sync",
            ["pytest"],
        ],
    ),
)


def call_option(option: MakeOption) -> None:
    logging.info(f"调用选项: mkp [green bold]{option.name}")
    if option.desc:
        logging.info(f"功能描述: [purple bold]{option.desc}")

    for command in option.commands:
        if isinstance(command, str):
            child_opt = MAKE_OPTIONS.get(command, None)
            if child_opt:
                logging.info(f"执行子命令: [purple]{child_opt.name}")
                call_option(child_opt)
            else:
                logging.error(f"未找到匹配选项: {command}")
                return
        elif isinstance(command, list):
            cli.run_cmd(command)  # type: ignore
        elif callable(command):
            command()
        else:
            logging.error(f"非法命令: [red]{option.name} -> {command}")


OPTIONS = "/".join(MAKE_OPTIONS.keys())


@cli.app.command()
def main(optstr: str = Argument(help=f"构建选项[{OPTIONS}]")):
    found_option = MAKE_OPTIONS.get(optstr, None)
    if found_option:
        call_option(found_option)
    else:
        logging.error(f"未找到匹配选项: {optstr}")
