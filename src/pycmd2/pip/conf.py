from __future__ import annotations

from typing import ClassVar

from pycmd2.common.cli import get_client
from pycmd2.common.config import TomlConfigMixin

cli = get_client()


class PipConfig(TomlConfigMixin):
    """Pip配置."""

    NAME = "pip"

    TRUSTED_PIP_URL: ClassVar[list[str]] = [
        "--trusted-host",
        "pypi.tuna.tsinghua.edu.cn",
        "-i",
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
    ]


conf = PipConfig()
