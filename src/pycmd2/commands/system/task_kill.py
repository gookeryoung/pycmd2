"""功能: 结束进程.

命令: taskk [PROC]
"""

from __future__ import annotations

import fnmatch
import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import List

from typer import Argument
from typing_extensions import Annotated

from pycmd2.client import get_client

cli = get_client()
logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """进程信息类."""

    name: str
    pid: str


class TaskKillProcessor:
    """任务结束处理类."""

    def __init__(self) -> None:
        self.process_list: list[ProcessInfo] = []

    def get_matched_process(self, process_name: str) -> List[ProcessInfo]:
        """获取匹配的进程列表.

        Returns:
            List[ProcessInfo]: 匹配的进程列表
        """
        return [p for p in self.process_list if fnmatch.fnmatch(p.name.lower(), process_name.lower())]

    def get_process_list(self) -> None:
        """获取进程列表."""
        if sys.platform == "win32":
            self._get_process_list_windows()
        else:
            self._get_process_list_unix()

    def _get_process_list_windows(self, encoding: str = "gbk") -> None:
        try:
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                encoding=encoding,
                check=True,
            )
            logger.debug(f"已使用{encoding}解码")
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split('","')
                    if len(parts) >= 2:  # noqa: PLR2004
                        name = parts[0].strip('"')
                        pid = parts[1].strip('"')
                        self.process_list.append(ProcessInfo(name, pid))
        except (UnicodeDecodeError, subprocess.CalledProcessError):  # 更具体的异常类型
            if encoding == "utf8":
                logger.exception("获取进程列表失败")
                return

            # 如果GBK编码失败, 尝试UTF-8
            try:
                self._get_process_list_windows(encoding="utf8")
                logger.debug("已使用utf8解码")
            except (subprocess.SubprocessError, OSError, ValueError):
                logger.exception("获取进程列表失败")
                return

    def _get_process_list_unix(self) -> None:
        try:
            result = subprocess.run(
                ["ps", "-eo", "pid,comm", "--no-headers"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) >= 2:  # noqa: PLR2004
                        pid = parts[0]
                        name = parts[1]
                        self.process_list.append(ProcessInfo(name, pid))
        except (subprocess.SubprocessError, OSError, ValueError):
            logger.exception("获取进程列表失败")
            return

    def kill_process(self, process_name: str) -> None:
        """结束进程.

        Args:
            process_name (str): 进程名
        """
        self.get_process_list()
        matched_processes = self.get_matched_process(process_name)

        if not matched_processes:
            logger.warning(f"未找到进程 {process_name}")
            return

        logger.info(f"找到 {len(matched_processes)} 个匹配 '{process_name}' 的进程: {[m.name for m in matched_processes]}")
        try:
            success_count = 0
            for process in matched_processes:
                if self._kill_process_by_pid(process.pid):
                    logger.info(f"成功终止进程 {process.name} (PID: {process.pid})")
                    success_count += 1
                else:
                    logger.info(f"无法终止进程 {process.name} (PID: {process.pid})")
        except (subprocess.SubprocessError, OSError, ValueError):
            logger.exception("终止进程失败")
            return
        else:
            logger.info(f"成功终止 {success_count} 个匹配 '{process_name}' 的进程")

    def _kill_process_by_pid(self, pid: str) -> bool:
        if sys.platform == "win32":
            return self._kill_process_by_pid_windows(pid)

        return self._kill_process_by_pid_unix(pid)

    def _kill_process_by_pid_windows(self, pid: str) -> bool:
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

    def _kill_process_by_pid_unix(self, pid: str) -> bool:
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
    processor = TaskKillProcessor()
    processor.kill_process(proc)
