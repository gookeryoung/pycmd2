import logging
import subprocess
import threading
from typing import List

from rich.logging import RichHandler

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


def run_cmd(commands: List[str]):
    """
    执行命令并实时记录输出到日志。
    """
    # 启动子进程，设置文本模式并启用行缓冲
    logging.info(f"调用命令: [green bold]{commands}")

    proc = subprocess.Popen(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,  # 手动解码
    )

    # 创建并启动记录线程
    stdout_thread = threading.Thread(target=log_stream, args=(proc.stdout, logging.info))
    stderr_thread = threading.Thread(target=log_stream, args=(proc.stderr, logging.error))
    stdout_thread.start()
    stderr_thread.start()

    # 等待进程结束
    proc.wait()

    # 等待所有输出处理完成
    stdout_thread.join()
    stderr_thread.join()

    # 检查返回码
    if proc.returncode != 0:
        logging.error(f"命令执行失败，返回码：{proc.returncode}")
