"""功能: 实现类似 ssh-copy-id 的功能."""

import logging
import subprocess
import sys
from pathlib import Path

import typer

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


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
        ValueError: 参数错误
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
            # 安全警告: StrictHostKeyChecking=no 会禁用主机密钥验证
            # 仅在可信网络环境中使用此选项
            logger.warning(
                "安全警告: 正在禁用SSH主机密钥验证, 请确保在可信网络环境中使用",
            )

            # 验证输入参数
            if not hostname or not username or not password:
                msg = "主机名、用户名和密码不能为空"
                raise ValueError(msg)

            if port < 1 or port > 65535:  # noqa: PLR2004
                msg = f"无效的端口号: {port}, 必须在1-65535范围内"
                raise ValueError(msg)

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
                    "-o",
                    "UserKnownHostsFile=/dev/null",  # 避免污染known_hosts文件
                    "-o",
                    "ConnectTimeout=10",  # 添加连接超时
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
            logger.exception(
                "未找到sshpass工具, 请先安装sshpass或使用系统自带的ssh-copy-id命令"
                "安装方法:"
                "Ubuntu/Debian: sudo apt-get install sshpass"
                "CentOS/RHEL: sudo yum install sshpass"
                "macOS: brew install hudochenkov/sshpass/sshpass"
                "或者直接使用: ssh-copy-id -p {port} {username}@{hostname}",
            )
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
    # 参数验证
    if not hostname or not username or not password:
        logger.error("主机名、用户名和密码不能为空")
        msg = "主机名、用户名和密码不能为空"
        raise typer.BadParameter(msg)

    if port < 1 or port > 65535:  # noqa: PLR2004
        logger.error(f"无效的端口号: {port}, 必须在1-65535范围内")
        msg = "端口号必须在1-65535范围内"
        raise typer.BadParameter(msg)

    # 验证公钥文件
    expanded_path = Path(keypath).expanduser()
    if not expanded_path.exists():
        logger.error(f"公钥文件不存在: {expanded_path}")
        msg = f"公钥文件不存在: {keypath}"
        raise typer.BadParameter(msg)

    if not expanded_path.is_file():
        logger.error(f"指定的路径不是文件: {expanded_path}")
        msg = f"指定的路径不是文件: {keypath}"
        raise typer.BadParameter(msg)

    ssh_copy_id(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        public_key_path=keypath,
    )
