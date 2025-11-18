"""功能: 结束进程.

命令: taskk [PROC]
"""

from __future__ import annotations

import fnmatch
import logging
import subprocess
import sys
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


def get_process_list_windows() -> List[dict]:  # noqa: C901
    """获取Windows系统进程列表.

    Returns:
        List[dict]: 进程列表
    """
    try:
        # 使用tasklist命令获取进程信息
        result = subprocess.run(
            ["tasklist", "/fo", "csv", "/nh"],
            capture_output=True,
            text=True,
            encoding="gbk",  # Windows中文系统通常使用GBK编码
            check=True,
        )
        processes = []
        for line in result.stdout.strip().split("\n"):
            if line:
                # 解析CSV格式的输出
                parts = line.split('","')
                if len(parts) >= 2:  # noqa: PLR2004
                    name = parts[0].strip('"')
                    pid = parts[1].strip('"')
                    processes.append({"name": name, "pid": pid})
    except (UnicodeDecodeError, subprocess.CalledProcessError):  # 更具体的异常类型
        # 如果GBK编码失败, 尝试UTF-8
        try:
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                check=True,
            )
            processes = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split('","')
                    if len(parts) >= 2:  # noqa: PLR2004
                        name = parts[0].strip('"')
                        pid = parts[1].strip('"')
                        processes.append({"name": name, "pid": pid})
        except (subprocess.SubprocessError, OSError, ValueError):
            logger.exception("获取进程列表失败")
            return []
        else:
            return processes
    except (subprocess.SubprocessError, OSError, ValueError):  # 更具体的异常类型
        logger.exception("获取进程列表失败")
        return []
    else:
        return processes


def get_process_list_unix() -> List[dict]:
    """获取Unix/Linux系统进程列表.

    Returns:
        List[dict]: 进程列表
    """
    try:
        # 使用ps命令获取进程信息
        result = subprocess.run(
            ["ps", "-eo", "pid,comm", "--no-headers"],
            capture_output=True,
            text=True,
            check=True,
        )
        processes = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.strip().split(maxsplit=1)
                if len(parts) >= 2:  # noqa: PLR2004
                    pid = parts[0]
                    name = parts[1]
                    processes.append({"name": name, "pid": pid})
    except (subprocess.SubprocessError, OSError, ValueError):  # 更具体的异常类型
        logger.exception("获取进程列表失败")
        return []
    else:
        return processes


def match_process_name(process_name: str, pattern: str) -> bool:
    """检查进程名是否匹配通配符模式.

    Returns:
        bool: 是否匹配.
    """
    return fnmatch.fnmatch(process_name.lower(), pattern.lower())


def kill_process_by_pid_windows(pid: str) -> bool:
    """在Windows上通过PID终止进程.

    Returns:
        bool: 是否成功终止进程.
    """
    try:
        subprocess.run(
            ["taskkill", "/F", "/PID", pid],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.exception(f"终止进程PID {pid} 失败")
        return False
    else:
        return True


def kill_process_by_pid_unix(pid: str) -> bool:
    """在Unix/Linux上通过PID终止进程.

    Returns:
        bool: 是否成功终止进程.
    """
    try:
        subprocess.run(
            ["kill", "-9", pid],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.exception(f"终止进程PID {pid} 失败")
        return False
    else:
        return True


@cli.app.command()
def main(
    proc: Annotated[str, Argument(help="待结束进程(支持通配符)")],
) -> None:
    try:
        # 根据操作系统选择不同的实现
        if sys.platform.startswith("win"):
            processes = get_process_list_windows()
            kill_func = kill_process_by_pid_windows
        else:
            processes = get_process_list_unix()
            kill_func = kill_process_by_pid_unix

        # 查找匹配的进程
        matched_processes = [process for process in processes if match_process_name(process["name"], proc)]

        if not matched_processes:
            logger.info(f"未找到匹配 '{proc}' 的进程")
            return

        # 终止所有匹配的进程
        success_count = 0
        for process in matched_processes:
            if kill_func(process["pid"]):
                logger.info(f"成功终止进程 {process['name']} (PID: {process['pid']})")
                success_count += 1
            else:
                logger.error(f"终止进程 {process['name']} (PID: {process['pid']}) 失败")

        logger.info(f"成功终止 {success_count} 个匹配 '{proc}' 的进程")

    except (subprocess.SubprocessError, OSError, ValueError):
        logger.exception(f"结束进程 {proc} 失败!")
    else:
        logger.info(f"结束进程 {proc} 完成!")
