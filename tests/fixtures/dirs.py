import logging
from pathlib import Path

import pytest


@pytest.fixture
def dir_tests():
    dir_tests = Path(__file__).parent.parent
    logging.info(f"测试目录: {dir_tests}")
    return dir_tests
