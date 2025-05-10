"""功能：初始化 python 环境变量"""

import logging
import re
from pathlib import Path

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import IS_WINDOWS

cli = setup_client()

# 用户文件夹
home_dir = Path.home()

# pip 配置信息
pip_conf_content = """[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
[install]
trusted-host = tuna.tsinghua.edu.cn
"""


def _add_env_to_bashrc(
    variable: str,
    value: str,
    comment: str = "",
):
    """
    安全添加环境变量到.bashrc文件

    :param variable: 变量名 (如 "UV_INDEX_URL")
    :param value: 变量值 (如 "https://pypi.tuna.tsinghua.edu.cn/simple")
    :param comment: 可选注释说明
    """
    bashrc_path = Path.home() / ".bashrc"
    export_line = f'export {variable}="{value}"'
    entry = f"\n# {comment}\n{export_line}\n" if comment else f"\n{export_line}\n"  # noqa

    try:
        # 读取现有内容
        if bashrc_path.exists():
            content = bashrc_path.read_text(encoding="utf-8")
        else:
            content = ""

        # 检查是否已存在
        pattern = re.compile(
            r"^export\s+" + re.escape(variable) + r"=.*$",
            flags=re.MULTILINE,
        )

        if pattern.search(content):
            logging.warning(f"已存在 {variable} 配置，跳过添加")
            return False

        # 追加新条目并处理末尾换行
        if content and content[-1] != "\n":
            entry = "\n" + entry.lstrip()

        with bashrc_path.open("a", encoding="utf-8") as f:
            f.write(entry)

        logging.info(f"成功添加 {variable} 到 {bashrc_path}")
        return True

    except Exception as e:
        logging.error(f"❌ 操作失败: {str(e)}")
        return False


def setup_uv() -> None:
    logging.info("配置 uv 环境变量")

    uv_envs = dict(
        UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple",
        UV_DEFALT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple",
        UV_HTTP_TIMEOUT=60,
        UV_LINK_MODE="copy",
    )

    if IS_WINDOWS:
        for k, v in uv_envs.items():
            run_cmd(["setx", str(k), str(v)])
    else:
        for k, v in uv_envs.items():
            _add_env_to_bashrc(str(k), str(v))


def setup_pip() -> None:
    pip_dir = home_dir / "pip" if IS_WINDOWS else home_dir / ".pip"
    pip_conf = pip_dir / "pip.ini" if IS_WINDOWS else pip_dir / "pip.conf"

    if not pip_dir.exists():
        logging.info(f"创建 pip 文件夹: [green bold]{pip_dir}")
        pip_dir.mkdir(parents=True)
    else:
        logging.info(f"已存在 pip 文件夹: [green bold]{pip_dir}")

    logging.info(f"写入文件: [green bold]{pip_conf}")
    pip_conf.write_text(pip_conf_content)


@cli.app.command()
def main():
    setup_pip()
    setup_uv()
