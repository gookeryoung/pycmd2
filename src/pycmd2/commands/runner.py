from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import List

from pycmd2.client import get_client

logger = logging.getLogger(__name__)


class BaseRunner:
    """BaseRunner 基类."""

    DESCRIPTION: str = ""
    CHILD_RUNNERS: ClassVar[dict[str, BaseRunner]] = {}
    SUBCOMMANDS: ClassVar[List[List[str] | str | Callable[..., Any]]] = []

    def run(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """执行系列命令."""
        cli = get_client()

        if self.DESCRIPTION:
            logger.info(f"功能描述: [green b]{self.DESCRIPTION}")
        else:
            logger.error("功能描述为空, 退出")
            return

        if not self.SUBCOMMANDS:
            logger.info("没有子命令, 退出")
            return

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand.lower() not in self.CHILD_RUNNERS:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                self.CHILD_RUNNERS[subcommand.lower()].run()
            elif isinstance(subcommand, list):
                cli.run_cmd(list(subcommand))
            elif isinstance(subcommand, Callable):
                logger.info(f"执行可调用对象: [purple b]{subcommand.__name__}")
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")

    @property
    def name(self) -> str:
        """获取执行器名称."""
        return self.__class__.__name__.replace("Runner", "").lower()


class SubcommandRunnerMixin(BaseRunner):
    """子命令执行器."""

    SUBCOMMANDS: ClassVar[list[list[str] | str | Callable[..., Any]]] = []

    def run(self) -> None:
        """执行子命令."""
        cli = get_client()

        logger.info(f"调用: {__class__.__name__}")

        if not self.SUBCOMMANDS:
            logger.error("子命令为空, 退出")
            return None

        for subcommand in self.SUBCOMMANDS:
            if isinstance(subcommand, str):
                if subcommand.lower() not in self.CHILD_RUNNERS:
                    logger.error(f"未找到执行器: {subcommand}")
                    continue

                logger.info(f"执行子命令: {subcommand}")
                self.CHILD_RUNNERS[subcommand.lower()].run()
            elif isinstance(subcommand, list):
                cli.run_cmd(list(subcommand))
            elif isinstance(subcommand, Callable):
                logger.info(f"执行可调用对象: [purple b]{subcommand.__name__}")
                subcommand()
            else:
                logger.error(f"未知子命令: {subcommand}")

        return super().run()


class SequenceRunnerMixin(BaseRunner):
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


class ParallelRunnerMixin(BaseRunner):
    """并行执行器."""

    def run(
        self,
        func: Callable[..., Any],
        args: List[Any],
        max_workers: int = 10,
    ) -> None:
        """执行操作."""
        super().run()

        t0 = perf_counter()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(func, args)

            for result in results:
                logger.info(
                    f"调用: {func.__name__}({max_workers}个线程), 执行结果: {result}, "
                    f"耗时: {perf_counter() - t0:.4f}s",
                )


class SubcommandRunner(SubcommandRunnerMixin, BaseRunner):
    """默认执行器."""


class SequenceRunner(SequenceRunnerMixin, BaseRunner):
    """默认序列执行器."""


class ParallelRunner(ParallelRunnerMixin, BaseRunner):
    """默认并行执行器."""
