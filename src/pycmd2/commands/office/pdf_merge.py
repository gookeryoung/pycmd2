"""功能: 合并当前目录下所有 pdf 文件, 最多包含两层目录."""

from __future__ import annotations

import dataclasses
import logging
from functools import lru_cache
from pathlib import Path

import pypdf

from pycmd2.client import get_client
from pycmd2.commands.office.pdf_crypt import is_encrypted

cli = get_client(help_doc="pdf 合并工具.")
logger = logging.getLogger(__name__)

# 跳过的文件名或者文件夹名
IGNORED_FOLDERS = [".git", "__pycache__"]

# 合并后的文件名前缀
MERGE_MARK = "合并#"
# 最大搜索深度
MAX_SEARCH_DEPTH = 2

page_num = 0


@dataclasses.dataclass
class PdfFileInfo:
    """pdf 文件信息."""

    prefix: str
    files: list[Path]
    children: list[PdfFileInfo]
    page_count: int = 0

    def count(self) -> int:
        """计算文件数量.

        Returns:
            int: 文件数量
        """
        return len(self.files) + sum(x.count() for x in self.children)

    def merge_file_info(
        self,
        info: PdfFileInfo,
        root_dir: Path,
        writer: pypdf.PdfWriter,
    ) -> None:
        """按照 PdfFileInfo 进行合并.

        Args:
            info (PdfFileInfo): 已搜索 PDFInfo
            root_dir (Path): 根目录
            writer (pypdf.PdfWriter): PdfWriter
        """
        root_bookmark = writer.add_outline_item(info.prefix, 0) if info.prefix else None

        def _merge_pdf_file(filepath: Path) -> None:
            with filepath.open("rb") as pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                writer.append(filepath.as_posix(), import_outline=False)
                writer.add_outline_item(
                    filepath.stem,
                    self.page_count,
                    parent=root_bookmark,
                )
                self.page_count += len(reader.pages)

        cli.run(_merge_pdf_file, self.files)

        for child_info in self.children:
            self.merge_file_info(child_info, root_dir, writer=writer)

    def __str__(self) -> str:
        """打印信息.

        Returns:
            str: 打印信息
        """
        fs = [x.name for x in self.files]
        return f"prefix={self.prefix}, files={fs}, children={self.children}"

    def __repr__(self) -> str:
        """打印信息.

        Returns:
            str: 打印信息
        """
        return self.__str__()


def relative_depth(search_dir: Path, root_dir: Path) -> int:
    """搜索文件夹相对根文件夹深度.

    Parameters:
        search_dir (Path): 当前搜索目录
        root_dir (Path): 根目录

    Returns:
        int: 搜索深度
    """
    try:
        relative_path = search_dir.relative_to(root_dir)
        return len(relative_path.parts)
    except ValueError:
        return 0


@lru_cache(maxsize=128)
def search_directory(
    search_dir: Path,
    root_dir: Path,
) -> PdfFileInfo | None:
    """搜索目录下的所有pdf文件.

    Args:
        search_dir (Path): 当前搜索目录
        root_dir (Path): 根目录

    Returns:
        PdfFileInfo | None: 搜索到的 PdfFileInfo
    """
    if relative_depth(search_dir, root_dir) > MAX_SEARCH_DEPTH:
        return None

    children: list[PdfFileInfo] = []
    folders = [d for d in sorted(search_dir.iterdir()) if d.is_dir() and d.name not in IGNORED_FOLDERS]
    for folder in folders:
        pdf_info = search_directory(folder, root_dir)
        if pdf_info is not None:
            children.append(pdf_info)

    pdf_files = [x for x in sorted(search_dir.glob("*.pdf")) if not is_encrypted(x) and MERGE_MARK not in x.stem]
    if not pdf_files and not children:
        return None

    prefix = search_dir.relative_to(root_dir).name
    return PdfFileInfo(prefix=prefix, files=pdf_files, children=children)


@cli.app.command()
def main() -> None:
    pdf_info = search_directory(cli.cwd, cli.cwd)
    if not pdf_info or pdf_info.count() <= 1:
        logger.error("PDF files not found, exit")
        return

    writer = pypdf.PdfWriter()
    pdf_info.merge_file_info(pdf_info, cli.cwd, writer=writer)

    target_filepath = cli.cwd / f"{MERGE_MARK}{cli.cwd.stem}.pdf"
    with target_filepath.open("wb") as pdf_file:
        writer.write(pdf_file)
        writer.close()

    logger.info(f"[*] 写入到文件[{target_filepath.name}]")
