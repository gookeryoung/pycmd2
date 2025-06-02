from typing import List

from pycmd2.common.cli import get_client
from pycmd2.common.config import TomlConfigMixin

cli = get_client()


class PipConfig(TomlConfigMixin):
    NAME = "pip"

    TRUSTED_PIP_URL: List[str] = [
        "--trusted-host",
        "pypi.tuna.tsinghua.edu.cn",
        "-i",
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
    ]


conf = PipConfig()
