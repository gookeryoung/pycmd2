import logging

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")


pytest_plugins = [
    "tests.fixtures.cli",
    "tests.fixtures.dirs",
]
