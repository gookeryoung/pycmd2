import logging
import platform

import chardet
from rich.logging import RichHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="[*] %(message)s",
    handlers=[RichHandler(markup=True)],
)
logger = logging.getLogger(__name__)


class StreamDecoder:
    def __init__(self, logger_func, min_bytes=100):
        self.logger_func = logger_func
        self.min_bytes = min_bytes  # 检测编码所需最小字节数
        self._buffer = b""  # 缓冲二进制数据
        self._encoding = None  # 最终确定的编码

    def _detect_encoding(self):
        """通过缓冲数据检测编码"""
        if len(self._buffer) < self.min_bytes:
            return None
        result = chardet.detect(self._buffer[: self.min_bytes])
        self._encoding = result["encoding"] or "utf-8"
        logger.debug(f"检测到编码: {self._encoding} (置信度: {result['confidence']:.2f})")
        return self._encoding

    def feed(self, data):
        """接收二进制数据并处理"""
        if not data:
            return
        self._buffer += data

        # 如果编码未确定，尝试检测
        if not self._encoding:
            if self._detect_encoding() is None:
                return  # 数据不足，等待下一次输入

        # 按已确定的编码解码
        try:
            text = self._buffer.decode(self._encoding)
            if "\n" not in text:
                return  # 等待更多数据直到有换行符
            lines = text.split("\n")
            for line in lines[:-1]:  # 最后一行可能不完整
                if line.strip():
                    self.logger_func(line.strip())
            self._buffer = lines[-1].encode(self._encoding)  # 保留未完成部分
        except UnicodeDecodeError:
            logger.warning(f"解码失败: [red]{self._encoding}[/], 退回到 [green]utf-8")
            self._encoding = "utf-8"  # 回退到 UTF-8


def stream_reader(stream, logger_func):
    """读取流并使用动态编码解码"""
    decoder = StreamDecoder(logger_func)
    default_encoding = "gbk" if platform.system() == "Windows" else "utf8"

    while True:
        data = stream.read(1024)  # 每次读取 1KB 二进制数据
        if not data:
            if decoder._buffer:
                try:
                    text = decoder._buffer.decode(decoder._encoding or default_encoding)
                    if text.strip():
                        logger_func(text.strip())
                except UnicodeDecodeError as e:
                    logger.error(f"Unicode解码错误: [red]{e}")
            break
        decoder.feed(data)
    stream.close()
