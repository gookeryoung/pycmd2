import logging
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def dir_tests() -> Path:
    dir_tests = Path(__file__).parent.parent
    logger.info(f"测试目录: {dir_tests}")
    return dir_tests
