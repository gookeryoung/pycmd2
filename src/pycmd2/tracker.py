import logging
from functools import wraps
from time import perf_counter
from typing import Callable
from typing import TypeVar

from rich.logging import RichHandler
from typing_extensions import ParamSpec

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])

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
