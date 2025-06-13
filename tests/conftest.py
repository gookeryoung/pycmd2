from __future__ import annotations

import logging

import pytest

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")

logger = logging.getLogger(__name__)

pytest_plugins = [
    "tests.fixtures.cli",
    "tests.fixtures.dirs",
    "tests.fixtures.config",
]

slow_tests = []


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="需要 --runslow 选项")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> None:
    """自动添加slow标记."""
    if call.when == "call":
        runtime = call.duration
        if runtime > 1.0:  # 阈值设为1秒
            item.add_marker(pytest.mark.slow)
            slow_tests.append((item.name, runtime))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    if slow_tests:
        logger.info("\n慢测试报告:")
        for name, time in slow_tests:
            logger.info(f"{name}: {time:.2f}s")
    else:
        logger.info("没有慢测试!")
