"""控制命令行工具."""

from __future__ import annotations

import concurrent.futures
import logging
import os
import platform
import shutil
import subprocess
import threading
from pathlib import Path
from time import perf_counter
from typing import Any
from typing import Callable
from typing import IO
from typing import Sequence

import typer
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)


def _log_stream(
    stream: IO[bytes],
    logger_func: Callable[[str], None],
) -> None:
    # 读取字节流
    for line_bytes in iter(stream.readline, b""):
        try:
            # 尝试UTF-8解码
            line = line_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            # 尝试GBK解码并替换错误字符
            line = line_bytes.decode("gbk", errors="replace").strip()
        if line:
            logger_func(line)
    stream.close()


def _setup_pyqt(*, enable_high_dpi: bool = False) -> None:
    """初始化 PyQt5 环境."""
    import os  # noqa: PLC0415

    import PyQt5  # noqa: PLC0415
    from PyQt5.QtCore import Qt  # noqa: PLC0415
    from PyQt5.QtWidgets import QApplication  # noqa: PLC0415

    qt_dir = Path(PyQt5.__file__).parent
    plugin_path = qt_dir / "plugins" / "platforms"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)

    if enable_high_dpi:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # noqa: FBT003
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # noqa: FBT003


class Client:
    """命令工具."""

    def __init__(
        self,
        app: typer.Typer,
        console: Console,
        *,
        enable_qt: bool = False,
        enable_high_dpi: bool = False,
    ) -> None:
        self.app = app
        self.console = console

        if enable_qt:
            _setup_pyqt(enable_high_dpi=enable_high_dpi)

    @property
    def cwd(self) -> Path:
        """当前工作目录."""
        return Path.cwd()

    @property
    def home(self) -> Path:
        """用户目录."""
        return Path.home()

    @property
    def settings_dir(self) -> Path:
        """用户配置目录."""
        env_path = os.environ.get("PYCMD2_HOME", None)
        if env_path is not None:
            return Path(env_path)

        return self.home / ".pycmd2"

    @property
    def is_windows(self) -> bool:
        """是否为 Windows 系统."""
        return platform.system() == "Windows"

    @staticmethod
    def run(
        func: Callable[..., Any],
        args: Sequence[Any] | None = None,
    ) -> None:
        """并行调用命令.

        Args:
            func (Callable[..., Any]): 被调用函数, 支持任意数量参数
            args (Optional[Iterable[Any]], optional): 调用参数, 默认值 `None`.
        """
        if not callable(func):
            logger.error(f"对象不可调用, 退出: [red]{func.__name__}")
            return

        if not args:
            logger.info(f"缺少多个执行目标, 取消多线程: [red]args={args}")
            func()
            return

        t0 = perf_counter()
        returns: list[concurrent.futures.Future[Any]] = []

        logger.info(f"Start threads, targets: [green]{len(args)}[/]")
        with concurrent.futures.ThreadPoolExecutor() as t:
            for arg in args:
                logger.info(f"Start Processing: [green bold]{arg!s}")
                returns.append(t.submit(func, arg))
        logger.info(
            f"Close threads, time used: "
            f"[green bold]{perf_counter() - t0:.4f}s.",
        )

    @staticmethod
    def run_cmd(
        commands: list[str],
    ) -> None:
        """执行命令并实时记录输出到日志.

        Args:
            commands (List[str]): 命令列表

        Raises:
            FileNotFoundError: 找不到命令
        """
        t0 = perf_counter()
        # 启动子进程, 设置文本模式并启用行缓冲
        logger.info(f"调用命令: [green bold]{commands}")

        proc_path = shutil.which(commands[0])
        if not proc_path:
            msg = f"找不到命令: {commands[0]}"
            raise FileNotFoundError(msg)

        proc = subprocess.Popen(
            [proc_path, *commands[1:]],
            stdin=None,  # 继承父进程的stdin, 允许用户输入
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 手动解码
        )

        # 创建并启动记录线程
        stdout_thread = threading.Thread(
            target=_log_stream,
            args=(proc.stdout, logging.info),
        )
        stderr_thread = threading.Thread(
            target=_log_stream,
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
            logger.error(f"命令执行失败, 返回码: {proc.returncode}")

        logger.info(f"用时: [green bold]{perf_counter() - t0:.4f}s.")

    @staticmethod
    def run_cmdstr(
        cmdstr: str,
    ) -> None:
        """直接执行命令, 用于避免输出重定向.

        Args:
            cmdstr (str): 命令参数, 如: `ls -la`
        """
        t0 = perf_counter()
        logger.info(f"调用命令: [green bold]{cmdstr}")
        try:
            subprocess.run(
                cmdstr,  # 直接使用 Shell 语法
                shell=True,
                check=True,  # 检查命令是否成功
            )
        except subprocess.CalledProcessError as e:
            msg = f"命令执行失败, 返回码: {e.returncode}"
            logger.exception(msg)
        else:
            total = perf_counter() - t0
            logger.info(f"调用命令成功, 用时: [green bold]{total:.4f}s.")


def get_client(
    help_doc: str = "",
    *,
    enable_qt: bool = False,
    enable_high_dpi: bool = False,
) -> Client:
    """创建 cli 程序.

    Args:
        help_doc (str, optional): 描述文件
        enable_qt (bool, optional): 是否启用 Qt. Defaults to False.
        enable_high_dpi (bool, optional): 是否启用高 DPI. Defaults to False.

    Returns:
        Client: 获取实例
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[*] %(message)s",
        handlers=[RichHandler(markup=True)],
    )

    return Client(
        app=typer.Typer(help=help_doc),
        console=Console(),
        enable_qt=enable_qt,
        enable_high_dpi=enable_high_dpi,
    )
