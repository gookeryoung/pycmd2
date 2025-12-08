from __future__ import annotations

import builtins
import contextlib
import logging
import platform
import time
from pathlib import Path
from typing import List

import typer

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.runner import MultiCommandRunner
from pycmd2.runner import ParallelRunner


class DocDiffConfig(TomlConfigMixin):
    """文档对比配置."""

    DOC_DIFF_TITLE = "对比结果"


cli = get_client(help_doc="MS Office文档对比工具.")
conf = DocDiffConfig()
logger = logging.getLogger(__name__)


def diff_doc(old: Path, new: Path) -> None:
    """使用win32 api对比文档."""
    if not old.exists():
        logger.error(f"旧文件不存在: {old}")
        return

    if not new.exists():
        logger.error(f"新文件不存在: {new}")
        return

    try:
        import win32com.client as win32  # type: ignore # noqa: PLC0415
    except ImportError:
        logger.exception("win32com.client 未安装, 退出.")
        return

    word = win32.gencache.EnsureDispatch("Word.Application")  # type: ignore
    word.Visible = False  # 在后台运行Word
    word.DisplayAlerts = False  # 禁用警告

    try:
        doc_old = word.Documents.Open(str(old))
        logger.info(f"打开旧文件: [u green]{old}")

        doc_new = word.Documents.Open(str(new))
        logger.info(f"打开新文件: [u green]{new}")

        # 使用word.CompareDocuments方法比较文档
        doc_compare = word.CompareDocuments(doc_old, doc_new)

        # Save the comparison result
        output = new.parent / f"{conf.DOC_DIFF_TITLE}@{time.strftime('%H_%M_%S')}.docx"

        if doc_compare:
            doc_compare.SaveAs2(str(output))
            doc_compare.Close()
            logger.info(f"Compare completed. Save to: {output}")
        else:
            logger.error(f"Compare {old} and {new} failed!")

    except Exception:
        logger.exception(f"Compare {old} and {new} failed!")
    finally:
        try:
            # Close all opened documents
            for doc in word.Documents:
                doc.Close(SaveChanges=False)
        except Exception:
            logger.exception("Close document failed!")

        with contextlib.suppress(builtins.BaseException):
            word.Quit()

        # Close Word process after quitting
        MultiCommandRunner().run(["taskkill", "/f", "/t", "/im", "WINWORD.EXE"])


@cli.app.command()
def main(
    files: List[Path] = typer.Argument(help="待输入文件清单"),  # noqa: B008
) -> None:
    """Compare two doc/docx files."""
    if platform.system() != "Windows":
        logger.error("This tool is only available on Windows.")
        return

    if len(files) < 2:  # noqa: PLR2004
        logger.error("Input file list must have at least 2 files.")
        return

    old_file, new_file = files[0], files[1]
    ParallelRunner().run(lambda: diff_doc(old_file, new_file))
