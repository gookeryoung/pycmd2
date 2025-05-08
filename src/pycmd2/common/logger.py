import logging

from rich.logging import RichHandler


def setup_logging():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="[*] %(message)s",
        handlers=[RichHandler(markup=True)],
    )


def log_stream(stream, logger_func):
    for line_bytes in iter(stream.readline, b""):  # 读取字节流
        try:
            line = line_bytes.decode("utf-8").strip()  # 尝试UTF-8解码
        except UnicodeDecodeError:
            line = line_bytes.decode("gbk", errors="replace").strip()  # 尝试GBK解码并替换错误字符
        if line:
            logger_func(line)
    stream.close()
