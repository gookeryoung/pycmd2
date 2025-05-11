"""
功能: 合并当前目录下所有 pdf 文件, 最多包含两层目录.
"""

import dataclasses
import logging
from functools import lru_cache
from pathlib import Path
from typing import List
from typing import Optional

import pypdf

from pycmd2.common.cli import get_client
from pycmd2.office.pdf_crypt import is_encrypted

cli = get_client(help="pdf 合并工具.")

# 跳过的文件名或者文件夹名
IGNORED_FOLDERS = [".git", "__pycache__"]

# 合并后的文件名前缀
MERGE_MARK = "合并#"
# 最大搜索深度
MAX_SEARCH_DEPTH = 2

page_num = 0


@dataclasses.dataclass
class PdfFileInfo:
    prefix: str
    files: List[Path]
    children: List["PdfFileInfo"]

    def count(self) -> int:
        return len(self.files) + sum([x.count() for x in self.children])

    def __str__(self):
        fs = list(x.name for x in self.files)
        return f"prefix={self.prefix}, files={fs}, children={self.children}"

    def __repr__(self):
        return self.__str__()


def relative_depth(search_dir: Path, root_dir: Path) -> int:
    """搜索文件夹相对根文件夹深度"""
    try:
        relative_path = search_dir.relative_to(root_dir)
        return len(relative_path.parts)
    except ValueError:
        return 0


@lru_cache(maxsize=128)
def search_directory(
    search_dir: Path,
    root_dir: Path,
) -> Optional[PdfFileInfo]:
    """搜索目录下的所有pdf文件

    Args:
        search_dir (Path): 当前搜索目录
        root_dir (Path): 根目录

    Returns:
        Optional[PdfFileInfo]: pdf 文件信息
    """
    if relative_depth(search_dir, root_dir) > MAX_SEARCH_DEPTH:
        return None

    children: List[PdfFileInfo] = []
    folders = [
        d
        for d in sorted(search_dir.iterdir())
        if d.is_dir() and d.name not in IGNORED_FOLDERS
    ]
    for folder in folders:
        pdf_info = search_directory(folder, root_dir)
        if pdf_info is not None:
            children.append(pdf_info)

    pdf_files = list(
        x
        for x in sorted(search_dir.glob("*.pdf"))
        if not is_encrypted(x) and MERGE_MARK not in x.stem
    )
    if not len(pdf_files) and not len(children):
        return None

    prefix = search_dir.relative_to(root_dir).name
    return PdfFileInfo(prefix=prefix, files=pdf_files, children=children)


def merge_file_info(info: PdfFileInfo, root_dir: Path, writer: pypdf.PdfWriter):
    """按照 PdfFileInfo 进行合并

    Args:
        info (PdfFileInfo): 已搜索 PDFInfo
        root_dir (Path): 根目录
        writer (pypdf.PdfWriter): PdfWriter
    """
    if info.prefix:
        root_bookmark = writer.add_outline_item(info.prefix, 0)
    else:
        root_bookmark = None

    def _merge_pdf_file(filepath: Path):
        global page_num
        with open(filepath.as_posix(), "rb") as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            writer.append(filepath.as_posix(), import_outline=False)
            writer.add_outline_item(
                filepath.stem,
                page_num,
                parent=root_bookmark,
            )
            page_num += len(reader.pages)

    cli.run(_merge_pdf_file, info.files)

    for child_info in info.children:
        merge_file_info(child_info, root_dir, writer=writer)


@cli.app.command()
def main():
    pdf_info = search_directory(cli.CWD, cli.CWD)
    if not pdf_info or pdf_info.count() <= 1:
        logging.error("[*] 未发现待合并文件, 退出...")
        return

    writer = pypdf.PdfWriter()
    merge_file_info(pdf_info, root_dir=cli.CWD, writer=writer)

    target_filepath = cli.CWD / f"{MERGE_MARK}{cli.CWD.stem}.pdf"
    with open(target_filepath, "wb") as pdf_file:
        writer.write(pdf_file)
        writer.close()

    print(f"[*] 写入到文件[{target_filepath.name}]")
