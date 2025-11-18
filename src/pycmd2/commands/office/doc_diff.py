from __future__ import annotations

import builtins
import contextlib
import logging
import time
from pathlib import Path
from typing import List

import typer
import win32com.client as win32

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class DocDiffConfig(TomlConfigMixin):
    """Docdiff config."""

    DOC_DIFF_TITLE = "对比结果"


cli = get_client(help_doc="Diff tool for ms office documents.")
conf = DocDiffConfig()
logger = logging.getLogger(__name__)


def diff_doc(old: Path, new: Path) -> None:
    """Diff doc using win32 api."""
    if not old.exists():
        logger.error(f"Old file not exist: {old}")
        return

    if not new.exists():
        logger.error(f"New file not exist: {new}")
        return

    word = win32.gencache.EnsureDispatch("Word.Application")  # type: ignore
    word.Visible = False  # Run word in background
    word.DisplayAlerts = False  # Disable alerts

    try:
        doc_old = word.Documents.Open(str(old))
        logger.info(f"Open old file: [u green]{old}")

        doc_new = word.Documents.Open(str(new))
        logger.info(f"Open new file: [u green]{new}")

        # Compare documents using word.CompareDocuments method
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
        cli.run_cmd(["taskkill", "/f", "/t", "/im", "WINWORD.EXE"])


@cli.app.command()
def main(
    files: List[Path] = typer.Argument(help="待输入文件清单"),  # noqa: B008
) -> None:
    """Compare two doc/docx files."""
    if len(files) < 2:  # noqa: PLR2004
        logger.error("Input file list must have at least 2 files.")
        return

    old_file, new_file = files[0], files[1]
    cli.run(lambda: diff_doc(old_file, new_file))
