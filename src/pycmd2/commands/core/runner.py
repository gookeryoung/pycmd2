from __future__ import annotations

import logging
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import IO
from typing import List
from typing import Optional
from typing import Sequence

logger = logging.getLogger(__name__)


class Runner:
    """空执行器."""

    def run(self) -> None:
        """执行操作."""
        logger.info(f"调用Runner: [green b]{type(self).__name__}")


class DescriptionRunnerMixin(Runner):
    """描述执行器."""

    DESCRIPTION: str = ""

    def run(self) -> None:
        """执行操作."""
        super().run()

        if self.DESCRIPTION:
            logger.info(f"功能描述: [green b]{self.DESCRIPTION}")


class SequenceRunnerMixin(Runner):
    """序列执行器."""

    def run_before(self) -> None:
        """执行前操作."""

    def run_after(self) -> None:
        """执行后操作."""

    def run(self) -> None:
        """执行操作."""
        self.run_before()
        super().run()
        self.run_after()


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
    try:
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
    except ValueError:
        logger.exception("无法读取流数据")


class CommandRunnerMixin(Runner):
    """字符串命令执行器."""

    def run(
        self,
        command: str,
        executable: str | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """执行操作."""
        super().run()

        if not shutil.which(command):
            logger.warning(f"找不到命令: {command}")
            return

        t0 = perf_counter()
        logger.info(f"调用命令: [green bold]{command}")
        try:
            subprocess.run(
                command,  # 直接使用 Shell 语法
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


class MultiCommandRunnerMixin(Runner):
    """字符串命令执行器."""

    def run(self, commands: List[str]) -> None:
        """执行操作.

        Raises:
            FileNotFoundError: 找不到命令
        """
        super().run()

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


class SubcommandRunnerMixin(MultiCommandRunnerMixin, Runner):
    """子命令执行器."""

    CHILD_RUNNERS: ClassVar[dict[str, Runner]] = {}
    SUBCOMMANDS: ClassVar[list[list[str] | str | Callable[..., Any]]] = []

    def run(self) -> None:
        """执行子命令."""
        if not self.SUBCOMMANDS:
            logger.error("子命令为空, 退出")
            return

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand.lower() not in self.CHILD_RUNNERS:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                self.CHILD_RUNNERS[subcommand.lower()].run()
            elif isinstance(subcommand, list):
                super().run(subcommand)
            elif isinstance(subcommand, Callable):
                logger.info(f"执行可调用对象: [purple b]{subcommand.__name__}")
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")


class ParallelRunnerMixin(Runner):
    """并行执行器."""

    def run(
        self,
        func: Callable[..., Any],
        args: Optional[List[Any]] = None,
        max_workers: int = 10,
    ) -> Sequence[Any]:
        """执行操作.

        Returns:
            List[Any]: 执行结果
        """
        super().run()

        if not callable(func):
            logger.error(f"func 必须是一个可调用对象: {func=}")
            return []

        func_name = func.__name__ if hasattr(func, "__name__") else "Unknown"
        logger.info(f"调用: {func_name}({args=})")

        if not args:
            logger.info("没有参数, 取消多线程...")
            return [func()]

        if not isinstance(args, List):
            logger.error(f"args 必须是一个列表: {args=}")
            return []

        if len(args) == 1:
            logger.info("只有一个参数, 取消多线程...")
            return [func(args[0])]

        t0 = perf_counter()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, args))

        logger.info(
            f"调用: {func_name}(args: {args!s})({max_workers}个线程), "
            f"耗时: {perf_counter() - t0:.4f}s",
        )
        return results


class CommandRunner(CommandRunnerMixin, Runner):
    """默认字符串命令执行器."""


class MultiCommandRunner(MultiCommandRunnerMixin, Runner):
    """默认字符串命令执行器."""


class SubcommandRunner(SubcommandRunnerMixin, Runner):
    """默认执行器."""


class DescSubcommandRunner(DescriptionRunnerMixin, SubcommandRunner, Runner):
    """默认执行器."""


class SequenceRunner(SequenceRunnerMixin, Runner):
    """默认序列执行器."""


class SequenceSubcommandRunner(SequenceRunnerMixin, SubcommandRunner, Runner):
    """默认序列执行器."""


class ParallelRunner(ParallelRunnerMixin, Runner):
    """默认并行执行器."""
