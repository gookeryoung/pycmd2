from __future__ import annotations

import logging
import os
import queue
import shutil
import subprocess
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
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

    @staticmethod
    def _safe_log_stream(stream: IO[bytes], logger_func: Callable[[str], None]) -> None:
        """安全地记录流数据, 处理各种异常情况.

        Args:
            stream: 字节流
            logger_func: 日志记录函数
        """
        if not stream:
            return

        try:
            # 读取字节流直到结束
            while True:
                try:
                    line_bytes = stream.readline()
                    if not line_bytes:  # 空字节表示流结束
                        break

                    try:
                        # 尝试UTF-8解码
                        line = line_bytes.decode("utf-8").strip()
                    except UnicodeDecodeError:
                        # 尝试GBK解码并替换错误字符
                        line = line_bytes.decode("gbk", errors="replace").strip()

                    if line:
                        logger_func(line)
                except (ValueError, AttributeError, OSError):
                    # 流可能已关闭或出现其他错误
                    logger.exception("读取流时出错")
                    break
        except Exception:
            logger.exception("日志流处理异常")

    def run(self, commands: List[str]) -> None:
        """执行操作.

        Raises:
            FileNotFoundError: 找不到命令
        """
        super().run()

        t0 = perf_counter()
        logger.info(f"调用命令: [green bold]{commands}")

        proc_path = shutil.which(commands[0])
        if not proc_path:
            msg = f"找不到命令: {commands[0]}"
            raise FileNotFoundError(msg)

        # 启动子进程
        proc = subprocess.Popen(
            [proc_path, *commands[1:]],
            stdin=None,  # 继承父进程的stdin, 允许用户输入
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 手动解码
        )

        # 创建并启动记录线程
        threads = []
        for stream, log_func in [
            (proc.stdout, logging.info),
            (proc.stderr, logging.warning),
        ]:
            thread = threading.Thread(
                target=self._safe_log_stream,
                args=(stream, log_func),
                daemon=True,  # 设置为守护线程，主程序退出时自动终止
            )
            thread.start()
            threads.append(thread)

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
            # 等待所有输出处理完成
            for thread in threads:
                thread.join(timeout=2)  # 减少等待时间，因为线程已经是守护线程

            # 安全地关闭流
            for stream in [proc.stdout, proc.stderr]:
                if stream:
                    with suppress(Exception):  # 忽略异常
                        stream.close()

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


class _OptimizedLogProcessor:
    """优化的日志处理器，使用队列减少线程开销."""

    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size
        self.log_queue: queue.Queue[tuple[Callable[[str], None], str]] = queue.Queue(
            maxsize=1000,
        )
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self._worker_thread.start()

    def _process_logs(self) -> None:
        """处理日志队列中的日志."""
        log_batch: list[tuple[Callable[[str], None], str]] = []

        while not self._stop_event.is_set():
            try:
                # 批量处理日志
                try:
                    log_func, message = self.log_queue.get(timeout=0.1)
                    log_batch.append((log_func, message))
                except queue.Empty:
                    if log_batch:
                        self._flush_batch(log_batch)
                        log_batch = []
                    continue

                if len(log_batch) >= self.batch_size:
                    self._flush_batch(log_batch)
                    log_batch = []

            except OSError:
                logger.exception("日志处理异常")

        # 处理剩余日志
        if log_batch:
            self._flush_batch(log_batch)

    def _flush_batch(self, log_batch: List[tuple[Callable[[str], None], str]]) -> None:
        """刷新日志批次."""
        for log_func, message in log_batch:
            try:
                log_func(message)
            except Exception:  # noqa: PERF203
                logger.exception("日志写入异常")

    def log(self, log_func: Callable[[str], None], message: str) -> None:
        """添加日志到队列."""
        try:
            self.log_queue.put_nowait((log_func, message))
        except queue.Full:
            # 队列满时，直接记录日志
            log_func(message)

    def stop(self) -> None:
        """停止日志处理器."""
        self._stop_event.set()
        self._worker_thread.join(timeout=2)


class _OptimizedStreamReader:
    """优化的流读取器，减少解码开销."""

    def __init__(self, log_processor: _OptimizedLogProcessor) -> None:
        self.log_processor = log_processor
        self._buffer_size = 8192  # 8KB缓冲区

    def read_stream(self, stream: IO[bytes], log_func: Callable[[str], None]) -> None:
        """优化的流读取方法."""
        if not stream:
            return

        try:
            while True:
                # 批量读取数据
                chunk = stream.read(self._buffer_size)
                if not chunk:
                    break

                # 一次性解码整个块
                try:
                    text = chunk.decode("utf-8")
                except UnicodeDecodeError:
                    text = chunk.decode("gbk", errors="replace")

                # 按行分割并记录
                lines = text.strip().split("\n")
                for line in lines:
                    if line.strip():
                        self.log_processor.log(log_func, line.strip())

        except Exception:
            logger.exception("流读取异常")


class OptimizedMultiCommandRunnerMixin(Runner):
    """优化的命令执行器."""

    def __init__(self) -> None:
        super().__init__()

        # 全局日志处理器实例
        self._log_processor = _OptimizedLogProcessor()
        # 命令路径缓存
        self._command_cache: dict[str, str] = {}
        # 注册清理函数
        weakref.finalize(self, self._cleanup)

    def _cleanup(self) -> None:
        """清理资源."""
        self._log_processor.stop()

    def _get_command_path(self, command: str) -> str:
        """获取命令路径（带缓存）.

        Returns:
            str: 命令路径，如果找不到则返回空字符串
        """
        if command not in self._command_cache:
            self._command_cache[command] = shutil.which(command) or ""
        return self._command_cache[command]

    def run(self, commands: List[str]) -> None:
        """优化的命令执行方法."""
        if not commands:
            return

        cmd_path = self._get_command_path(commands[0])
        if not cmd_path:
            logger.warning(f"找不到命令: {commands[0]}")
            return

        t0 = perf_counter()
        logger.info(f"调用命令: [green bold]{commands}")

        try:
            # 优化的子进程创建
            proc = subprocess.Popen(
                [cmd_path, *commands[1:]],
                stdin=None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                # 优化参数
                bufsize=8192,  # 设置缓冲区大小
                close_fds=True,  # 关闭不必要的文件描述符
            )

            # 创建优化的流读取器
            stream_reader = _OptimizedStreamReader(self._log_processor)

            # 创建线程处理输出
            threads = []
            for stream, log_func in [
                (proc.stdout, logger.info),
                (proc.stderr, logger.warning),
            ]:
                thread = threading.Thread(
                    target=stream_reader.read_stream,
                    args=(stream, log_func),
                    daemon=True,
                )
                thread.start()
                threads.append(thread)

            try:
                # 等待进程完成
                proc.wait(timeout=300)

                # 等待所有输出线程完成
                for thread in threads:
                    thread.join(timeout=2)

            except subprocess.TimeoutExpired:
                # 优雅终止进程
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                logger.exception("命令执行超时, 已强制终止")
                raise

            finally:
                # 清理资源
                for stream in [proc.stdout, proc.stderr]:
                    if stream:
                        with suppress(Exception):
                            stream.close()

            if proc.returncode != 0:
                logger.error(f"命令执行失败, 返回码: {proc.returncode}")

            logger.info(f"用时: [green bold]{perf_counter() - t0:.4f}s.")

        except Exception:
            logger.exception("命令执行异常")


class OptimizedParallelRunnerMixin(Runner):
    """优化的并行执行器，重用线程池."""

    def __init__(self) -> None:
        # 根据系统资源确定合理的线程数
        self.default_workers = min(32, (os.cpu_count() or 1) + 4)
        self._executor: Optional[ThreadPoolExecutor] = None
        self._executor_lock = threading.Lock()
        # 注册清理函数
        weakref.finalize(self, self._shutdown_executor)

    def _shutdown_executor(self) -> None:
        """关闭线程池."""
        with self._executor_lock:
            if self._executor:
                self._executor.shutdown(wait=False)
                self._executor = None

    def _get_executor(self, max_workers: int) -> ThreadPoolExecutor:
        """获取或创建线程池.

        Returns:
            ThreadPoolExecutor: 线程池实例
        """
        with self._executor_lock:
            if (
                self._executor is None
                or self._executor._max_workers != max_workers  # noqa: SLF001
                or self._executor._shutdown  # noqa: SLF001
            ):
                if self._executor:
                    self._executor.shutdown(wait=False)

                self._executor = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix="OptimizedParallel",
                )

        return self._executor

    def run(
        self,
        func: Callable[..., Any],
        args: Optional[List[Any]] = None,
        max_workers: Optional[int] = None,
    ) -> List[Any]:
        """优化的并行执行方法.

        Returns:
            List[Any]: 结果列表
        """
        if not callable(func):
            logger.error(f"func 必须是一个可调用对象: {func=}")
            return []

        if not args:
            logger.info("没有参数, 取消多线程...")
            return [func()]

        if not isinstance(args, List):
            logger.error(f"args 必须是一个列表: {args=}")
            return []

        if len(args) == 1:
            logger.info("只有一个参数, 取消多线程...")
            return [func(args[0])]

        workers = max_workers or self.default_workers
        executor = self._get_executor(workers)

        func_name = getattr(func, "__name__", "Unknown")
        logger.info(f"调用: {func_name}({args=})")

        t0 = perf_counter()
        try:
            results = list(executor.map(func, args))
        except Exception:
            logger.exception("并行执行异常")
            return []
        else:
            logger.info(
                f"调用: {func_name}(args: {len(args)}个任务, {workers}个线程), "
                f"耗时: {perf_counter() - t0:.4f}s",
            )
            return results


class OptimizedMultiCommandRunner(OptimizedMultiCommandRunnerMixin, Runner):
    """优化字符串命令执行器."""


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


class OptimizedParallelRunner(OptimizedParallelRunnerMixin, Runner):
    """优化并行执行器."""
