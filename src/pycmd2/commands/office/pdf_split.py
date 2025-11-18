"""功能: 拆分指定 pdf 文件为多个 pdf."""

from __future__ import annotations

import logging
from functools import partial
from pathlib import Path

import pypdf
from typer import Argument

from pycmd2.client import get_client
from pycmd2.commands.office.pdf_crypt import list_pdf

cli = get_client(help_doc="pdf 分割工具.")
logger = logging.getLogger(__name__)


def parse_range_list(
    rangestr: str,
) -> list[tuple[int, int]] | None:
    """分析分割参数.

    Args:
        rangestr (str): 分割参数字符串

    Returns:
        Optional[List[Tuple[int, int]]]: 分割参数列表
    """
    if not rangestr:
        return None

    ranges = [x.strip() for x in rangestr.split(",")]
    range_list: list[tuple[int, int]] = []
    for e in ranges:
        if "-" in e:
            start, end = e.split("-")
            range_list.append((int(start), int(end)))
        else:
            range_list.append((int(e), int(e)))
    return range_list


def split_pdf_file(
    filepath: Path,
    output_dir: Path,
    range_list: list[tuple[int, int]] | None,
) -> None:
    """按照范围进行分割.

    Args:
        filepath (Path): pdf 文件路径
        output_dir (Path): 输出路径
        range_list (Optional[List[Tuple[int, int]]]): 分割范围, 如: 1-2, 3, 4-5
    """
    with filepath.open("rb") as pdf_file:
        reader = pypdf.PdfReader(pdf_file)

        if range_list is None:
            range_list = [(_ + 1, _ + 1) for _ in range(len(reader.pages))]

        logger.info(f"分割文件: {filepath}, 范围列表: {range_list}")
        out_pdfs: list[Path] = [output_dir / f"{filepath.stem}#{b:03}-{e:03}{filepath.suffix}" for (b, e) in range_list]
        for out, (begin, end) in zip(out_pdfs, range_list):
            writer = pypdf.PdfWriter()
            for page_num in range(begin - 1, end):
                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])

            try:
                with out.open("wb") as fw:
                    writer.write(fw)
            except OSError as e:
                msg = f"写入文件失败: {out.name}, 错误信息: {e}"
                logger.exception(msg)
            else:
                logger.info(f"写入文件成功: {out.name}, 页码: {(begin, end)}")
            writer.close()


@cli.app.command()
def main(
    rangestr: str = Argument(default="", help="分割范围, 默认按单页分割"),
) -> None:
    """分割命令.

    Args:
        rangestr (str, optional): 分割范围
    """
    unecrypted_files, _ = list_pdf()
    if not unecrypted_files:
        logger.error(f"当前目录下没有未加密的 pdf: {cli.cwd}")
        return

    range_list = parse_range_list(rangestr)
    split_func = partial(
        split_pdf_file,
        output_dir=cli.cwd,
        range_list=range_list,
    )
    cli.run(split_func, unecrypted_files)
