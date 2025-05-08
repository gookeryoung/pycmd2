"""功能：python 项目用构建命令"""

import datetime
import logging
import re
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Union

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client

cli = setup_client()

MakeOption = NamedTuple("MakeOption", (("name", str), ("commands", List[Union[List[str], Callable]])))


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
                    r'^(\s*)(__build_date__)\s*=\s*[\'"]?(\d{4}-\d{2}-\d{2})[\'"]?\s*$',
                    flags=re.MULTILINE | re.IGNORECASE,
                )

                # 查找所有匹配项
                matches = pattern.findall(content)
                if not matches:
                    print("未找到 __build_date__ 定义")
                    return False

                # 替换日期（保留原有格式）
                new_content = pattern.sub(
                    lambda m: f"{m.group(1)}{m.group(2)} = {m.group(0).split('=')[1].split(m.group(3))[0]}{build_date}\n",
                    content,
                )

                # 检查是否需要更新
                if new_content == content:
                    print("构建日期已是最新，无需更新")
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


MAKE_OPTIONS: Dict[str, MakeOption] = dict(
    bump=MakeOption(
        name="bump",
        commands=[
            ["uvx", "--from", "bump2version", "bumpversion", "patch"],
            _update_build_date,
        ],
    )
)


@cli.app.command()
def main(option: str):
    found_option = MAKE_OPTIONS.get(option, None)
    if found_option:
        for command in found_option.commands:
            if isinstance(command, list):
                run_cmd(command)
            elif isinstance(command, Callable):
                command()
            else:
                logging.error(f"非法命令: [red]{found_option.name} -> {command}")
