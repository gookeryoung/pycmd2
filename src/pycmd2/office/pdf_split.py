"""
功能: 拆分指定 pdf 文件为多个 pdf
"""

import logging
import typing
from functools import partial
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple

import pypdf
from typer import Argument

from pycmd2.common.cli import get_client
from pycmd2.office.pdf_crypt import list_pdf

cli = get_client(help="pdf 分割工具.")


def parse_range_list(
    rangestr: str,
) -> Optional[List[Tuple[int, int]]]:
    """分析分割参数

    Args:
        rangestr (str): 分割参数字符串

    Returns:
        Optional[List[Tuple[int, int]]]: 分割参数列表
    """
    if not rangestr:
        return None

    ranges = list(x.strip() for x in rangestr.split(","))
    range_list: List[Tuple[int, int]] = []
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
    range_list: Optional[List[Tuple[int, int]]],
):
    """按照范围进行分割

    Args:
        filepath (Path): pdf 文件路径
        output_dir (Path): 输出路径
        range_list (Optional[List[Tuple[int, int]]]): 分割范围, 如: 1-2, 3, 4-5
    """
    with open(filepath, "rb") as pdf_file:
        reader = pypdf.PdfReader(pdf_file)

        if range_list is None:
            range_list = [(_ + 1, _ + 1) for _ in range(len(reader.pages))]

        logging.info(f"分割文件: {filepath}, 范围列表: {range_list}")
        out_pdfs: typing.List[Path] = list(
            output_dir / f"{filepath.stem}#{b:03}-{e:03}{filepath.suffix}"
            for (b, e) in range_list
        )
        for out, (begin, end) in zip(out_pdfs, range_list):
            writer = pypdf.PdfWriter()
            for page_num in range(begin - 1, end):
                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])

            try:
                with open(out, "wb") as fw:
                    writer.write(fw)
            except OSError as e:
                logging.error(f"写入文件失败: {out.name}, 错误信息: {e}")
            else:
                logging.info(f"写入文件成功: {out.name}, 页码: {(begin, end)}")
            writer.close()


@cli.app.command()
def main(
    rangestr: str = Argument(default="", help="分割范围, 默认按单页分割"),
):
    """分割命令

    Args:
        rangestr (str, optional): 分割范围
    """
    unecrypted_files, _ = list_pdf()
    if not unecrypted_files:
        logging.error(f"当前目录下没有未加密的 pdf: {cli.CWD}")
        return

    range_list = parse_range_list(rangestr)
    split_func = partial(
        split_pdf_file, output_dir=cli.CWD, range_list=range_list
    )
    cli.run(split_func, unecrypted_files)
