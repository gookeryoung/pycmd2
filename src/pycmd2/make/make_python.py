"""功能：python 项目用构建命令"""

import datetime
import logging
import re
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Union

from typer import Argument

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client

cli = setup_client()


MakeOption = NamedTuple(
    "MakeOption",
    (
        ("name", str),
        ("commands", List[Union[str, List[str], Callable[..., Any]]]),
    ),
)


def _update_build_date():
    build_date = datetime.datetime.now().strftime("%Y-%m-%d")
    src_dir = Path.cwd() / "src"
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


def _clean():
    dirs = ["dist", ".tox", ".coverage", "htmlcov"]
    for directory in dirs:
        run_cmd(["rm", "-rf", directory])


MAKE_OPTIONS: Dict[str, MakeOption] = dict(
    bump=MakeOption(
        name="bump",
        commands=[
            ["uvx", "--from", "bump2version", "bumpversion", "patch"],
            _update_build_date,
            ["git", "add", "*/**/__init__.py"],
        ],
    ),
    dist=MakeOption(
        name="dist",
        commands=[
            _clean,
            ["hatch", "build"],
        ],
    ),
    pub=MakeOption(
        name="publish",
        commands=[
            "bump",
            "dist",
            ["hatch", "publish"],
            ["gitp"],
        ],
    ),
)


def call_option(option: MakeOption) -> None:
    logging.info(f"调用选项: mkp [green bold]{option.name}")
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
            run_cmd(command)  # type: ignore
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
