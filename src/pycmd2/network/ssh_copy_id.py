"""功能: 实现类似 ssh-copy-id 的功能。"""

import os
from pathlib import Path

import paramiko
from typer import Argument

from pycmd2.common.cli import get_client

cli = get_client()


def ssh_copy_id(
    hostname: str,
    port: int,
    username: str,
    password: str,
    public_key_path: str = "~/.ssh/id_rsa.pub",
    timeout: int = 10,
) -> None:
    """
    实现类似 ssh-copy-id 的功能。

    参数：
    - hostname: 远程服务器地址
    - port: SSH 端口
    - username: 远程服务器用户名
    - password: 远程服务器密码
    - public_key_path: 本地公钥路径（默认 ~/.ssh/id_rsa.pub）
    - timeout: 连接超时时间（秒）
    """
    # 读取本地公钥内容
    expanded_path = os.path.expanduser(public_key_path)
    with open(expanded_path) as f:
        public_key = f.read().strip()

    # 建立 SSH 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, port, username, password, timeout=timeout)
    except paramiko.AuthenticationException as e:
        raise Exception("认证失败，请检查用户名或密码") from e
    except Exception as e:
        raise Exception(f"连接失败：{str(e)}") from e

    # 使用 SFTP 创建或更新 authorized_keys
    sftp = ssh.open_sftp()
    try:
        # 检查并创建 .ssh 目录
        try:
            sftp.stat(".ssh")
        except FileNotFoundError:
            sftp.mkdir(".ssh", mode=0o700)

        # 追加公钥到 authorized_keys
        authorized_keys_path = ".ssh/authorized_keys"
        try:
            existing_keys = sftp.file(authorized_keys_path, "r").read().decode()
        except FileNotFoundError:
            existing_keys = ""

        if public_key not in existing_keys:
            with sftp.file(authorized_keys_path, "a") as f:
                f.write(f"\n{public_key}\n")

        # 设置文件权限（仅当文件新创建时）
        sftp.chmod(authorized_keys_path, 0o600)
    finally:
        sftp.close()
        ssh.close()


@cli.app.command()
def main(
    hostname: str = Argument(help="目标 ip 地址"),
    username: str = Argument(help="用户名"),
    password: str = Argument(help="密码"),
    port: int = Argument(22, help="端口"),
    keypath: str = Argument(str(Path.home() / ".ssh/id_rsa.pub")),
):
    ssh_copy_id(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        public_key_path=keypath,
    )
