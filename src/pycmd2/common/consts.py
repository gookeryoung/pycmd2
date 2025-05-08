import platform
from typing import List

IS_WINDOWS = platform.system() == "Windows"

TRUSTED_PIP_URL: List[str] = [
    "--trusted-host",
    "pypi.tuna.tsinghua.edu.cn",
    "-i",
    "https://pypi.tuna.tsinghua.edu.cn/simple/",
]
