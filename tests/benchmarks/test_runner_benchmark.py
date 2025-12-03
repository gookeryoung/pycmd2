import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pycmd2.runner import MultiCommandRunner
from pycmd2.runner import OptimizedMultiCommandRunner
from pycmd2.runner import OptimizedParallelRunner
from pycmd2.runner import ParallelRunner


@pytest.mark.slow
@pytest.mark.benchmark(
    group="multi_command_runner",
    min_rounds=10,
)
class TestOptimizedMultiCommandRunner:
    """测试优化 MultiCommandRunner 命令运行器."""

    def test_original_command_runner(self, benchmark: BenchmarkFixture) -> None:
        """测试运行器."""
        runner = MultiCommandRunner()
        benchmark(runner.run, ["echo", "test"])

    def test_optimized_command_runner(self, benchmark: BenchmarkFixture) -> None:
        """测试并行运行器."""
        runner = OptimizedMultiCommandRunner()
        benchmark(runner.run, ["echo", "test"])


@pytest.mark.slow
@pytest.mark.benchmark(
    group="parallel_runner",
    min_rounds=10,
)
class TestOptimizedParallelRunner:
    """测试优化 ParallelRunner 并行运行器."""

    def test_original_parallel_runner(self, benchmark: BenchmarkFixture) -> None:
        """测试运行器."""
        runner = ParallelRunner()
        benchmark(runner.run, lambda x: x * x, [1, 2, 3])

    def test_optimized_parallel_runner(self, benchmark: BenchmarkFixture) -> None:
        """测试并行运行器."""
        runner = OptimizedParallelRunner()
        benchmark(runner.run, lambda x: x * x, [1, 2, 3])
