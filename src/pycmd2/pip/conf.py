from __future__ import annotations

from typing import ClassVar

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin

cli = get_client()


class PipConfig(TomlConfigMixin):
    """Pip配置."""

    NAME = "pip"

    TRUSTED_PIP_URL: ClassVar[list[str]] = [
        "--trusted-host",
        "mirrors.aliyun.com",
        "-i",
        "http://mirrors.aliyun.com/pypi/simple/",
    ]


conf = PipConfig()
