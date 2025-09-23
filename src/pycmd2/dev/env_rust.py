"""功能: 初始化 python 环境变量."""

from __future__ import annotations

import logging
import platform

from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.dev.env_python import add_env_to_bashrc

cli = get_client()
logger = logging.getLogger(__name__)

# pip 配置信息
CARGO_CONF_CONTENT = """[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
"""


def setup_rustup(*, override: bool = True) -> None:
    logger.info("配置 uv 环境变量")

    rustup_envs: dict[str, str] = {
        "RUSTUP_UPDATE_ROOT": "https://mirrors.ustc.edu.cn/rust-static/rustup",
        "RUSTUP_DIST_SERVER": "https://mirrors.ustc.edu.cn/rust-static",
    }

    if cli.is_windows:
        for k, v in rustup_envs.items():
            cli.run_cmd(["setx", str(k), str(v)])
    else:
        for k, v in rustup_envs.items():
            add_env_to_bashrc(str(k), str(v), override=override)


def setup_cargo() -> None:
    cargo_dir = cli.home / ".cargo"
    cargo_conf = cargo_dir / "config.toml"

    if not cargo_dir.exists():
        logger.info(f"创建 pip 文件夹: [green bold]{cargo_dir}")
        cargo_dir.mkdir(parents=True)
    else:
        logger.info(f"已存在 pip 文件夹: [green bold]{cargo_dir}")

    logger.info(f"写入文件: [green bold]{cargo_conf}")
    cargo_conf.write_text(CARGO_CONF_CONTENT)


@cli.app.command()
def main(
    *,
    override: Annotated[bool, Option(help="是否覆盖已存在选项")] = True,
) -> None:
    setup_rustup(override=override)
    setup_cargo()

    machine = (
        "x86_64"
        if platform.machine().lower() in {"x86_64", "amd64"}
        else "i686"
    )

    if cli.is_windows:
        cli.run_cmdstr(
            f"wget https://static.rust-lang.org/rustup/dist/{machine}-pc-windows-msvc/rustup-init.exe",
        )
    else:
        cli.run_cmdstr(
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
        )
