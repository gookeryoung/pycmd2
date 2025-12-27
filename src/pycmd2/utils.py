from __future__ import annotations

import shutil
import socket
from functools import wraps
from time import perf_counter
from typing import Callable
from typing import Optional
from typing import TypeVar

import typer
from typing_extensions import ParamSpec

# 尝试导入psutil，如果失败则设置标志
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

P = ParamSpec("P")
R = TypeVar("R")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """计算函数运行时间.

    Args:
        func (Callable[P, R]): 被装饰的函数

    Returns:
        Callable[P, R]: 装饰后的函数
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """计算函数运行时间.

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            R: 函数返回值
        """
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        typer.echo(f"函数 `{func.__name__}` 用时 {end - start:.3f} s")
        return result

    return wrapper


def check_proc_by_name(proc_name: str) -> bool:
    """检查进程是否存在."""
    if not PSUTIL_AVAILABLE:
        typer.echo("psutil 模块未安装, 无法检查进程是否存在", err=True)
        return False

    try:
        for proc in psutil.process_iter(["pid", "name"]):
            if proc_name.lower() in proc.info["name"].lower():
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    else:
        return False


def check_port_available(host: str, port: int) -> bool:
    """检查端口是否可用."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # 0表示连接成功，说明端口被占用
    except OSError:
        return False


def check_command_available(cmd: str) -> bool:
    """检查可执行文件是否存在."""
    return shutil.which(cmd) is not None


def call_command(cmd: str, kill_func: Optional[Callable[[str], None]] = None) -> None:
    """调用命令行工具.

    Args:
        cmd: 命令名称
        kill_func: 自定义的进程终止函数，如果为None则使用默认的kill_process
    """
    # 检查命令是否存在
    if not check_command_available(cmd):
        typer.echo(f"命令 `{cmd}` 不存在, 请先安装命令", err=True)
        return

    # 检查进程是否存在
    if check_proc_by_name(cmd):
        typer.echo(f"进程 `{cmd}` 正在运行, 先停止进程...", err=True)
        if kill_func:
            kill_func(cmd)
        else:
            kill_proc(cmd)


def kill_proc(proc_name: str) -> None:
    """杀死进程."""
    if not PSUTIL_AVAILABLE:
        typer.echo("psutil 模块未安装, 无法杀死进程", err=True)
        return

    killed_count = 0
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            if proc_name.lower() in proc.info["name"].lower():
                proc.kill()
                killed_count += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        typer.echo(f"无法终止进程 `{proc.info['name']}`", err=True)
    else:
        if killed_count > 0:
            typer.echo(f"已终止 {killed_count} 个 `{proc_name}` 进程")


def kill_proc_by_pid(pid: int) -> None:
    """杀死进程."""
    if not PSUTIL_AVAILABLE:
        typer.echo("psutil 模块未安装, 无法杀死进程", err=True)
        return

    try:
        proc = psutil.Process(pid)
        proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        typer.echo(f"无法终止进程 `{proc.info['name']}`", err=True)
    else:
        typer.echo(f"已终止 `{proc.info['name']}` 进程: {proc.info['name']}")


def kill_proc_by_port(port: int) -> None:
    """杀死进程."""
    if not PSUTIL_AVAILABLE:
        typer.echo("psutil 模块未安装, 无法杀死进程", err=True)
        return

    try:
        for proc in psutil.process_iter(["pid", "name", "net_connections"]):
            if proc.info["net_connections"]:
                for conn in proc.info["net_connections"]:
                    if conn.laddr.port == port:
                        proc.kill()
                        typer.echo(
                            f"已终止 `{proc.info['name']}` 进程, "
                            f"pid: {proc.info['pid']}, "
                            f"port: {port}",
                        )
                        return
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        typer.echo(f"无法终止进程 `{proc.info['name']}`", err=True)
