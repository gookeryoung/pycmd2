"""功能：初始化 python 环境变量"""

import logging
from pathlib import Path

from typer import Option

from pycmd2.common.cli import run_cmd
from pycmd2.common.cli import setup_client
from pycmd2.common.consts import IS_WINDOWS
from pycmd2.envs.env_python import add_env_to_bashrc

cli = setup_client()

# 用户文件夹
HOME_DIR = Path.home()

# pip 配置信息
CARGO_CONF_CONTENT = """# 字节跳动
[source.crates-io]
replace-with = 'rsproxy'

[source.rsproxy]
registry = "https://rsproxy.cn/crates.io-index"

# 稀疏索引，要求 cargo >= 1.68
[source.rsproxy-sparse]
registry = "sparse+https://rsproxy.cn/index/"

[registries.rsproxy]
index = "https://rsproxy.cn/crates.io-index"

[net]
git-fetch-with-cli = true
"""


def setup_rustup(override: bool = True) -> None:
    logging.info("配置 uv 环境变量")

    rustup_envs = dict(
        RUSTUP_UPDATE_ROOT="https://rsproxy.cn",
        RUSTUP_DIST_SERVER="https://pypi.tuna.tsinghua.edu.cn/simple",
    )

    if IS_WINDOWS:
        for k, v in rustup_envs.items():
            run_cmd(["setx", str(k), str(v)])
    else:
        for k, v in rustup_envs.items():
            add_env_to_bashrc(str(k), str(v), override=override)


def setup_cargo() -> None:
    cargo_dir = HOME_DIR / ".cargo"
    cargo_conf = cargo_dir / "config.toml"

    if not cargo_dir.exists():
        logging.info(f"创建 pip 文件夹: [green bold]{cargo_dir}")
        cargo_dir.mkdir(parents=True)
    else:
        logging.info(f"已存在 pip 文件夹: [green bold]{cargo_dir}")

    logging.info(f"写入文件: [green bold]{cargo_conf}")
    cargo_conf.write_text(CARGO_CONF_CONTENT)


@cli.app.command()
def main(
    override: bool = Option(default=True, help="是否覆盖已存在选项"),
):
    setup_rustup(override=override)
    setup_cargo()
    if IS_WINDOWS:
        cli.run_cmdstr(
            "wget https://static.rust-lang.org/rustup/dist/i686-pc-windows-msvc/rustup-init.exe"
        )
    else:
        cli.run_cmdstr(
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        )
