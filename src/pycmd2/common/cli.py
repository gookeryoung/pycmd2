import concurrent.futures
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

import typer
from rich.console import Console

from pycmd2.common.logger import logger
from pycmd2.common.logger import stream_reader


@dataclass
class Client:
    app: typer.Typer
    console: Console


def setup_client() -> Client:
    """创建 cli 程序"""

    return Client(app=typer.Typer(), console=Console())


def run_cmd(command):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=False,
    )

    # 启动线程处理输出
    stdout_thread = threading.Thread(target=stream_reader, args=(proc.stdout, logger.info))
    stderr_thread = threading.Thread(target=stream_reader, args=(proc.stderr, logger.error))

    stdout_thread.start()
    stderr_thread.start()

    proc.wait()
    stdout_thread.join()
    stderr_thread.join()

    return proc.returncode


def run_parallel(func: Callable, args: Optional[List[Any]] = None):
    if not callable(func):
        logger.error(f"对象不可调用, 退出: [red]{func.__name__}")
        return

    if not args:
        logger.info(f"缺少多个执行目标, 取消多线程: [red]args={args}")
        func()

    t0 = time.perf_counter()
    rets: List[concurrent.futures.Future] = []

    logger.info(f"启动线程, 目标参数: [green]{len(args)}[/] 个")
    with concurrent.futures.ThreadPoolExecutor() as t:
        for arg in args:
            logger.info(f"开始处理: arg={str(arg)}")
            rets.append(t.submit(func, arg))
    logger.info("关闭线程")
    logger.info(f"用时: [green bold]{time.perf_counter() - t0:.4f}s.")
