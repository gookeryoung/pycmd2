"""功能: 初始化 python 环境变量."""

from __future__ import annotations

import logging
import re

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class EnvPythonConfig(TomlConfigMixin):
    """python 环境变量配置."""

    CONFIG_CONTENT = """[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
"""
    UV_DEFALT_INDEX = "http://mirrors.aliyun.com/pypi/simple/"
    UV_HTTP_TIMEOUT = 60
    UV_LINK_MODE = "copy"


cli = get_client()
conf = EnvPythonConfig(show_logging=False)
logger = logging.getLogger(__name__)

# 用户文件夹
BASHRC_PATH = cli.home / ".bashrc"


def add_env_to_bashrc(
    variable: str,
    value: str,
    comment: str = "",
    *,
    override: bool = False,
) -> bool:
    """安全添加或覆盖环境变量到.bashrc文件(优化空行问题).

    Parameters:
        variable: 变量名 (如 "UV_INDEX_URL")
        value: 变量值 (如 "http://mirrors.aliyun.com/pypi/simple/")
        comment: 可选注释说明
        override: 是否覆盖已有配置 (默认: False)

    Returns:
        操作是否成功.
    """
    export_line = f'export {variable}="{value}"'
    entry = f"\n# {comment}\n{export_line}\n" if comment else f"\n{export_line}\n"

    try:
        # 读取现有内容
        content = BASHRC_PATH.read_text(encoding="utf-8") if BASHRC_PATH.exists() else ""

        # 匹配现有配置的正则模式
        pattern = re.compile(
            r"^export\s+" + re.escape(variable) + r"=.*$",
            flags=re.MULTILINE,
        )

        if pattern.search(content):
            if override:
                # 改进点1: 删除旧配置及其后的空行.
                new_content = re.sub(pattern, "", content)

                # 改进点2: 清理多余空行(3+换行 -> 2换行).
                new_content = re.sub(r"\n{3,}", "\n\n", new_content)

                # 改进点3: 确保末尾换行后添加新条目.
                new_content = new_content.rstrip("\n") + "\n"
                new_content += entry.lstrip("\n")

                BASHRC_PATH.write_text(new_content, encoding="utf-8")
                logger.info(f"✅ 成功覆盖 {variable} 配置: {value}")
                return True
            logger.warning(f"⚠️ 已存在 {variable} 配置, 跳过添加")
            return False
        # 改进点4: 处理文件末尾空行后追加.
        if content:
            last_char = content[-1]
            entry = entry if last_char == "\n" else "\n" + entry.lstrip("\n")

        with BASHRC_PATH.open("a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"✅ 成功添加 {variable} 到 {BASHRC_PATH}")
    except OSError as e:
        msg = f"❌ 操作失败: [red]{e.__class__.__name__}: {e}"
        logger.exception(msg)
        return False
    else:
        return True


def write_pip_conf() -> None:
    """初始化 pip 配置."""
    pip_dir = cli.home / "pip" if cli.is_windows else cli.home / ".pip"
    pip_conf = pip_dir / "pip.ini" if cli.is_windows else pip_dir / "pip.conf"

    if not pip_dir.exists():
        logger.info(f"创建 pip 文件夹: [green bold]{pip_dir}")
        pip_dir.mkdir(parents=True)
    else:
        logger.info(f"已存在 pip 文件夹: [green bold]{pip_dir}")

    logger.info(f"写入文件: [green bold]{pip_conf}")
    pip_conf.write_text(conf.CONFIG_CONTENT)


def setup_uv_env(*, override: bool = True) -> None:
    """配置 uv 环境变量."""
    logger.info("配置 [purple bold]uv 环境变量")

    uv_envs = {k: v for k, v in conf.get_fileattrs().items() if k.startswith("UV_")}

    if cli.is_windows:
        for k, v in uv_envs.items():
            cli.run_cmd(["setx", str(k), str(v)])
    else:
        for k, v in uv_envs.items():
            add_env_to_bashrc(str(k), str(v), override=override)


def write_pypirc(token: str) -> None:
    """永久配置 PyPI Token."""
    token_file = cli.home / ".pypirc"
    if token_file.exists():
        logger.info(f"已存在 [green bold]{token_file}, 移除旧文件")
        token_file.unlink()

    logger.info(f"创建 [green bold]{token_file}")
    token_file.write_text(
        f"[pypi]\nusername = __token__\npassword = {token}\n",
        encoding="utf-8",
    )


@cli.app.command()
def main(
    pypi_token: str = typer.Argument(help="PyPI token值", default=""),
    *,
    override: bool = typer.Option(help="是否覆盖已存在选项", default=True),
) -> None:
    write_pip_conf()
    setup_uv_env(override=override)

    if pypi_token:
        logger.info("设置 [purple bold]pypi token")
        write_pypirc(pypi_token)
