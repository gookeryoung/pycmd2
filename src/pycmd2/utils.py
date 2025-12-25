import logging
import shutil
import socket
from functools import wraps
from time import perf_counter
from typing import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

logger = logging.getLogger(__name__)

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
        logger.info(
            f"函数 `{func.__name__}` 用时 {end - start:.3f} s",
        )
        return result

    return wrapper


def check_proc_by_name(proc_name: str) -> bool:
    """检查进程是否存在."""
    try:
        import psutil
    except ImportError:
        logger.warning("psutil 模块未安装, 无法检查进程是否存在")
        return False

    for proc in psutil.process_iter(["pid", "name"]):
        if proc_name.lower() in proc.info["name"].lower():
            return True
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
