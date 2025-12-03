from __future__ import annotations

from typing import Callable
from typing import List

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pycmd2.runner import MultiCommandRunner
from pycmd2.runner import OptimizedMultiCommandRunner
from pycmd2.runner import OptimizedParallelRunner
from pycmd2.runner import ParallelRunner

try:
    import numpy as np
except ImportError:
    np = None


@pytest.mark.slow
@pytest.mark.benchmark(
    group="multi_command_runner",
)
@pytest.mark.parametrize(
    "commands",
    [["echo", "test"], ["ls", "-la"], ["pwd"], ["date"], ["whoami"], ["uname", "-a"]],
)
class TestOptimizedMultiCommandRunner:
    """测试优化 MultiCommandRunner 命令运行器."""

    def test_original_multicommand_runner(
        self,
        benchmark: BenchmarkFixture,
        commands: List[str],
    ) -> None:
        """测试运行器."""
        runner = MultiCommandRunner()
        benchmark(runner.run, commands)

    def test_optimized_multicommand_runner(
        self,
        benchmark: BenchmarkFixture,
        commands: List[str],
    ) -> None:
        """测试并行运行器."""
        runner = OptimizedMultiCommandRunner()
        benchmark(runner.run, commands)


@pytest.mark.slow
@pytest.mark.skipif(not np, reason="numpy 未安装, 跳过测试")
@pytest.mark.benchmark(
    group="parallel_runner",
)
@pytest.mark.parametrize(
    ("func", "args"),
    [
        (lambda x: x * np.sin(x), np.linspace(0, 10, 100)),  # type: ignore
        (lambda x: x**2 + 3 * x - 12, np.linspace(0, 10, 100)),  # type: ignore
        (lambda x: x**3 - 2 * x**2 + 3 * x - 4, np.linspace(0, 10, 100)),  # type: ignore
        (lambda x: x**4 - 3 * x**3 + 3 * x**2 - x, np.linspace(0, 10, 100)),  # type: ignore
    ],
)
class TestOptimizedParallelRunner:
    """测试优化 ParallelRunner 并行运行器."""

    def test_original_parallel_runner(
        self,
        benchmark: BenchmarkFixture,
        func: Callable,
        args: List[float],
    ) -> None:
        """测试运行器."""
        runner = ParallelRunner()
        benchmark(runner.run, func, args)

    def test_optimized_parallel_runner(
        self,
        benchmark: BenchmarkFixture,
        func: Callable,
        args: List[float],
    ) -> None:
        """测试并行运行器."""
        runner = OptimizedParallelRunner()
        benchmark(runner.run, func, args)
