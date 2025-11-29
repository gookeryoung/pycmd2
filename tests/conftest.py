from __future__ import annotations

import logging
import os
import tempfile

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
    """添加命令行选项."""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="运行慢速测试",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """修改测试项收集."""
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="需要 --runslow 选项")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> None:
    """自动生成测试报告."""
    if call.when == "call":
        runtime = call.duration
        if runtime > 1.0:  # 阈值设为1秒
            item.add_marker(pytest.mark.slow)
            slow_tests.append((item.name, runtime))


def pytest_sessionstart(session: pytest.Session) -> None:
    """测试会话开始."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        filename="test_session.log",
        filemode="w",
    )

    # 为pycmd2创建临时目录, 并将其设置为PYCMD2_HOME环境变量
    os.environ["PYCMD2_HOME"] = str(tempfile.mkdtemp("pycmd2_home"))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """测试会话结束."""
    if slow_tests:
        logger.info("\n慢速测试报告:")
        for name, time in slow_tests:
            logger.info(f"{name}: {time:.2f}s")
    else:
        logger.info("没有慢速测试!")
