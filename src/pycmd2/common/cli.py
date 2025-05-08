import concurrent.futures
import logging
import time
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

import typer
from rich.console import Console


@dataclass
class Client:
    app: typer.Typer
    console: Console


def setup_client() -> Client:
    """创建 cli 程序"""

    return Client(app=typer.Typer(), console=Console())


def run_parallel(func: Callable, args: Optional[List[Any]] = None):
    if not callable(func):
        logging.error(f"对象不可调用, 退出: [red]{func.__name__}")
        return

    if not args:
        logging.info(f"缺少多个执行目标, 取消多线程: [red]args={args}")
        func()

    t0 = time.perf_counter()
    rets: List[concurrent.futures.Future] = []

    logging.info(f"启动线程, 目标参数: [green]{len(args)}[/] 个")
    with concurrent.futures.ThreadPoolExecutor() as t:
        for arg in args:
            logging.info(f"开始处理: [green bold]{str(arg)}")
            rets.append(t.submit(func, arg))
    logging.info(f"关闭线程, 用时: [green bold]{time.perf_counter() - t0:.4f}s.")
