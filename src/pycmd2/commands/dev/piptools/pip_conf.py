from __future__ import annotations

from typing import ClassVar
from typing import List

from pycmd2.config import TomlConfigMixin


class PipToolsConfig(TomlConfigMixin):
    """PipTools配置."""

    NAME = "pip_tools"
    TRUSTED_PIP_URL: ClassVar[List[str]] = [
        "--trusted-host",
        "mirrors.aliyun.com",
        "-i",
        "http://mirrors.aliyun.com/pypi/simple/",
    ]


conf = PipToolsConfig()
