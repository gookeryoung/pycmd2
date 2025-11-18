"""功能: 实现类似 ssh-copy-id 的功能."""

import subprocess
import sys
from pathlib import Path

import typer

from pycmd2.client import get_client

cli = get_client()


class SSHAuthenticationError(Exception):
    """SSH认证失败异常."""


class SSHConnectionError(Exception):
    """SSH连接失败异常."""


def ssh_copy_id(
    hostname: str,
    port: int,
    username: str,
    password: str,
    public_key_path: str = "~/.ssh/id_rsa.pub",
) -> None:
    """实现类似 ssh-copy-id 的功能.

    Args:
        hostname: 远程服务器地址
        port: SSH 端口
        username: 远程服务器用户名
        password: 远程服务器密码
        public_key_path: 本地公钥路径(默认 ~/.ssh/id_rsa.pub)

    Raises:
        SSHAuthenticationError: 认证失败
        SSHConnectionError: 连接失败
        Exception: 其他异常
    """
    # 读取本地公钥内容
    expanded_path = Path(public_key_path).expanduser()
    try:
        with expanded_path.open() as f:
            pub_key = f.read().strip()
    except FileNotFoundError as e:
        msg = f"公钥文件未找到: {expanded_path}"
        raise SSHConnectionError(msg) from e
    except Exception as e:
        msg = f"读取公钥文件失败: {e!s}"
        raise SSHConnectionError(msg) from e

    try:
        # 使用 sshpass 执行远程命令
        try:
            # 尝试使用 sshpass 执行远程命令
            process = subprocess.run(
                [
                    "sshpass",
                    "-p",
                    password,
                    "ssh",
                    "-p",
                    str(port),
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"{username}@{hostname}",
                    f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
                    f"cd ~/.ssh && touch authorized_keys && "
                    f"chmod 600 authorized_keys && "
                    f'grep -qF "{pub_key.split()[0]}.*{pub_key.split()[1]}"'
                    f"authorized_keys 2>/dev/null || "
                    f'echo "{pub_key}" >> authorized_keys',
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if process.returncode != 0:
                if "Permission denied" in process.stderr:
                    msg = "认证失败, 请检查用户名或密码"
                    raise SSHAuthenticationError(msg)
                msg = f"SSH执行失败: {process.stderr}"
                raise Exception(msg)  # noqa: TRY002

        except FileNotFoundError:
            # 如果没有 sshpass, 提示用户使用系统自带的 ssh-copy-id 命令
            sys.exit(1)

    except subprocess.TimeoutExpired as e:
        msg = "SSH连接超时"
        raise SSHConnectionError(msg) from e
    except Exception as e:
        msg = f"SSH操作失败: {e!s}"
        raise SSHConnectionError(msg) from e


@cli.app.command()
def main(
    hostname: str = typer.Argument(help="目标 ip 地址"),
    username: str = typer.Argument(help="用户名"),
    password: str = typer.Argument(help="密码"),
    port: int = typer.Option(22, help="端口"),
    keypath: str = typer.Option(str(Path.home() / ".ssh/id_rsa.pub")),
) -> None:
    ssh_copy_id(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        public_key_path=keypath,
    )
