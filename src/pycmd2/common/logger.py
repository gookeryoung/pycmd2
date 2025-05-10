import logging
from typing import Callable
from typing import IO

from rich.logging import RichHandler


def setup_logging() -> None:
    """Setup logging config."""

    logging.basicConfig(
        level=logging.INFO,
        format="[*] %(message)s",
        handlers=[RichHandler(markup=True)],
    )


def log_stream(stream: IO[bytes], logger_func: Callable[[str], None]) -> None:
    # 读取字节流
    for line_bytes in iter(stream.readline, b""):
        try:
            # 尝试UTF-8解码
            line = line_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            # 尝试GBK解码并替换错误字符
            line = line_bytes.decode("gbk", errors="replace").strip()
        if line:
            logger_func(line)
    stream.close()
