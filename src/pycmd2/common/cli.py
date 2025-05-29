import concurrent.futures
import logging
import platform
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence

import typer
from rich.console import Console

from pycmd2.common.logger import log_stream
from pycmd2.common.logger import setup_logging


@dataclass
class Client:
    """命令工具"""

    app: typer.Typer
    console: Console

    # 常量
    CWD: Path = Path(".")
    HOME: Path = Path.home()
    SETTINGS_DIR: Path = HOME / ".pycmd2"
    IS_WINDOWS: bool = platform.system() == "Windows"

    def run(
        self,
        func: Callable[..., Any],
        args: Optional[Sequence[Any]] = None,
    ):
        """并行调用命令.

        Args:
            func (Callable[..., Any]): 被调用函数, 支持任意数量参数
            args (Optional[Iterable[Any]], optional): 调用参数, 默认值 `None`.
        """
        if not callable(func):
            logging.error(f"对象不可调用, 退出: [red]{func.__name__}")
            return

        if not args:
            logging.info(f"缺少多个执行目标, 取消多线程: [red]args={args}")
            func()
            return

        t0 = perf_counter()
        returns: List[concurrent.futures.Future[Any]] = []

        logging.info(f"启动线程, 目标参数: [green]{len(args)}[/] 个")
        with concurrent.futures.ThreadPoolExecutor() as t:
            for arg in args:
                logging.info(f"开始处理: [green bold]{str(arg)}")
                returns.append(t.submit(func, arg))
        logging.info(f"关闭线程, 用时: [green bold]{perf_counter() - t0:.4f}s.")

    def run_cmd(
        self,
        commands: List[str],
    ) -> None:
        """执行命令并实时记录输出到日志。

        Args:
            commands (List[str]): 命令列表
        """

        t0 = perf_counter()
        # 启动子进程，设置文本模式并启用行缓冲
        logging.info(f"调用命令: [green bold]{commands}")

        proc = subprocess.Popen(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 手动解码
        )

        # 创建并启动记录线程
        stdout_thread = threading.Thread(
            target=log_stream,
            args=(proc.stdout, logging.info),
        )
        stderr_thread = threading.Thread(
            target=log_stream,
            args=(proc.stderr, logging.warning),
        )
        stdout_thread.start()
        stderr_thread.start()

        # 等待进程结束
        proc.wait()

        # 等待所有输出处理完成
        stdout_thread.join()
        stderr_thread.join()

        # 检查返回码
        if proc.returncode != 0:
            logging.error(f"命令执行失败，返回码：{proc.returncode}")

        logging.info(f"用时: [green bold]{perf_counter() - t0:.4f}s.")

    def run_cmdstr(
        self,
        cmdstr: str,
    ) -> None:
        """直接执行命令, 用于避免输出重定向

        Args:
            cmdstr (str): 命令参数, 如: `ls -la`
        """
        t0 = perf_counter()
        logging.info(f"调用命令: [green bold]{cmdstr}")
        try:
            subprocess.run(
                cmdstr,  # 直接使用 Shell 语法
                shell=True,
                check=True,  # 检查命令是否成功
            )
        except Exception as e:
            logging.error(f"调用命令失败: [red]{e}")
        else:
            total = perf_counter() - t0
            logging.info(f"调用命令成功, 用时: [green bold]{total:.4f}s.")


def get_client(
    help: str = "",
) -> Client:
    """创建 cli 程序

    Args:
        help (str, optional): 描述文件

    Returns:
        Client: 获取实例
    """

    setup_logging()

    return Client(
        app=typer.Typer(help=help),
        console=Console(),
        CWD=Path.cwd(),
    )
