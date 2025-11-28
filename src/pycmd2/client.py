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
MAX_TARGET_COUNT = 5


def _log_stream(
    stream: IO[bytes],
    logger_func: Callable[[str], None],
) -> None:
    """记录流数据.

    Args:
        stream: 字节流
        logger_func: 日志记录函数
    """
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
    """初始化 PyQt5 环境.

    Args:
        enable_high_dpi (bool): 是否启用高DPI支持
    """
    import os  # noqa: PLC0415

    try:
        import PyQt5  # noqa: PLC0415
        from PyQt5.QtCore import Qt  # noqa: PLC0415
        from PyQt5.QtWidgets import QApplication  # noqa: PLC0415
    except ModuleNotFoundError:
        logger.exception("PyQt5 未安装, 请安装 PyQt5 以启用高 DPI 支持")
        return
    else:
        logger.info("已初始化 PyQt5 环境")

    qt_dir = Path(PyQt5.__file__).parent
    plugin_path = qt_dir / "plugins" / "platforms"
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)

    if enable_high_dpi:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


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
        """初始化客户端.

        Args:
            app: Typer应用实例
            console: 控制台实例
            enable_qt: 是否启用Qt
            enable_high_dpi: 是否启用高DPI支持
        """
        self.app = app
        self.console = console

        if enable_qt:
            _setup_pyqt(enable_high_dpi=enable_high_dpi)

    @property
    def cwd(self) -> Path:
        """当前工作目录.

        Returns:
            Path: 当前工作目录路径
        """
        return Path.cwd()

    @property
    def home(self) -> Path:
        """用户目录.

        Returns:
            Path: 用户主目录路径
        """
        return Path.home()

    @property
    def settings_dir(self) -> Path:
        """用户配置目录.

        Returns:
            Path: 用户配置目录路径
        """
        env_path = os.environ.get("PYCMD2_HOME", None)
        if env_path is not None:
            return Path(env_path)

        return self.home / ".pycmd2"

    @property
    def is_windows(self) -> bool:
        """是否为 Windows 系统.

        Returns:
            bool: 如果是Windows系统返回True, 否则返回False
        """
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

        logger.info(f"启动线程池, 目标: [green]{len(args)}[/]")
        with concurrent.futures.ThreadPoolExecutor() as t:
            returns.extend(t.submit(func, arg) for arg in args)

        info = (
            args
            if len(args) < MAX_TARGET_COUNT
            else f"[{args[:MAX_TARGET_COUNT]}]...({len(args)}个)"
        )
        logger.info(f"处理目标: [green bold]{info}")
        logger.info(
            f"关闭线程池, 共计用时: [green bold]{perf_counter() - t0:.4f}s.",
        )

    @staticmethod
    def run_cmd(
        commands: list[str],
        *,
        shell: bool = False,
    ) -> None:
        """执行命令并实时记录输出到日志.

        Args:
            commands (List[str]): 命令列表
            shell (bool, optional): 是否使用 shell 执行, 默认值 `False`.

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
            shell=shell,
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

        try:
            # 等待进程结束
            proc.wait(timeout=300)  # 添加超时防止无限等待
        except subprocess.TimeoutExpired:
            # 先尝试优雅终止进程
            proc.terminate()
            try:
                # 等待进程优雅退出
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果进程不响应终止信号，强制杀死
                proc.kill()
                proc.wait()  # 确保进程彻底结束
            logger.exception("命令执行超时, 已强制终止")
            raise
        finally:
            # 确保子进程资源被清理
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()

        # 等待所有输出处理完成
        stdout_thread.join(timeout=10)  # 添加线程超时
        stderr_thread.join(timeout=10)

        # 检查线程是否已结束，如果仍在运行则强制停止
        if stdout_thread.is_alive():
            logger.warning("stdout线程未能正常结束")
        if stderr_thread.is_alive():
            logger.warning("stderr线程未能正常结束")

        # 检查返回码
        if proc.returncode != 0:
            logger.error(f"命令执行失败, 返回码: {proc.returncode}")

        logger.info(f"用时: [green bold]{perf_counter() - t0:.4f}s.")

    @staticmethod
    def run_cmdstr(
        cmdstr: str,
        executable: str | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """直接执行命令, 用于避免输出重定向.

        Args:
            cmdstr (str): 命令参数, 如: `ls -la`
            executable (str | None, optional): 可执行文件路径, 默认值 `None`.
            env (dict[str, str] | None, optional): 环境变量, 默认值 `None`.
        """
        t0 = perf_counter()
        logger.info(f"调用命令: [green bold]{cmdstr}")
        try:
            subprocess.run(
                cmdstr,  # 直接使用 Shell 语法
                shell=True,
                check=True,  # 检查命令是否成功
                executable=executable,
                env=env,
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
