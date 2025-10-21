"""功能: 初始化 rust 环境变量."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.dev.env_python import add_env_to_bashrc


class EnvRustConfig(TomlConfigMixin):
    """Rust 环境配置."""

    # rust 环境配置内容
    CONFIG_CONTENT = """[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
"""

    RUSTUP_UPDATE_ROOT = "https://mirrors.ustc.edu.cn/rust-static/rustup"
    RUSTUP_DIST_SERVER = "https://mirrors.ustc.edu.cn/rust-static"

    DOWNLOAD_CMD_WINDOWS = "wget https://win.rustup.rs -O rustup-init.exe"
    DOWNLOAD_CMD_LINUX = (
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    )


cli = get_client()
conf = EnvRustConfig(show_logging=False)
logger = logging.getLogger(__name__)


def setup_rustup(*, override: bool = True) -> None:
    logger.info("配置 uv 环境变量")

    rustup_envs: dict[str, object] = {
        k: v for k, v in conf.get_fileattrs().items() if k.startswith("RUSTUP_")
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
    cargo_conf.write_text(conf.CONFIG_CONTENT)


def download_rustup() -> None:
    if cli.is_windows:
        cli.run_cmdstr(conf.DOWNLOAD_CMD_WINDOWS)
    else:
        cli.run_cmdstr(conf.DOWNLOAD_CMD_LINUX)


@cli.app.command()
def main(
    *,
    install_version: str = typer.Argument(
        help="安装的 rust 版本",
        default="nightly",
    ),
    override: bool = typer.Option(help="是否覆盖已存在选项", default=True),
) -> None:
    setup_rustup(override=override)
    setup_cargo()

    ext = ".exe" if cli.is_windows else ""
    rustup_init_name = f"rustup-init{ext}"
    rustup_init_file = Path.cwd() / rustup_init_name
    if not rustup_init_file.exists():
        download_rustup()
    else:
        logger.info(
            f"已存在 rustup 安装文件: [green bold]{rustup_init_file}",
        )
        try:
            cli.run_cmd([
                rustup_init_name,
                f"--default-toolchain={install_version}",
                "--no-modify-path",
                "--default-host",
                "x86_64-pc-windows-msvc"
                if cli.is_windows
                else "x86_64-unknown-linux-gnu",
            ])
        except OSError:
            logger.exception(f"运行 {rustup_init_name} 失败")
            logger.info(
                f"请手动运行 {rustup_init_name} 进行安装, "
                f"或者删除该文件后重新下载",
            )
