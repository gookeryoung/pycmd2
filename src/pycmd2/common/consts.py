import platform
from pathlib import Path
from typing import List

IS_WINDOWS = platform.system() == "Windows"

TRUSTED_PIP_URL: List[str] = [
    "--trusted-host",
    "pypi.tuna.tsinghua.edu.cn",
    "-i",
    "https://pypi.tuna.tsinghua.edu.cn/simple/",
]

# Directories paths
CWD = Path.cwd()
HOME_DIR = Path.home()
DEFAULT_CONFIG_DIR = Path.home() / ".pycmd2"
