"""
功能: 加密/解密当前路径下所有pdf文件。
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

from pycmd2.common.cli import run_parallel
from pycmd2.common.cli import setup_client

cli = setup_client(help="pdf 加密/解密工具.")
CWD = Path.cwd()


def encrypt_pdf(
    filepath: Path,
    password: str,
) -> Tuple[Path, Optional[Path]]:
    """加密单个pdf文件
    :param filepath: pdf文件路径
    :param password: 加密使用的密码
    :return 加密前, 后的文件路径
    """
    reader = pypdf.PdfReader(filepath)
    writer = pypdf.PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password=password,
        owner_password=password,
        use_128bit=True,
    )

    enc_pdf_file = filepath.with_suffix(".enc.pdf")
    try:
        with open(enc_pdf_file, "wb") as f:
            writer.write(f)
        return filepath, enc_pdf_file
    except OSError:
        logging.error("写入加密文件[{enc_pdf_file.name}]失败, 错误信息: {e}")
        return filepath, None


def decrypt_pdf(
    filepath: Path,
    password: str,
) -> typing.Tuple[Path, typing.Optional[Path]]:
    """
    解密 PDF 文件。

    :param filepath: 输入的加密 PDF 文件路径
    :param password: PDF 文件的密码
    """
    # 打开输入的 PDF 文件
    with open(filepath, "rb") as f:
        reader = pypdf.PdfReader(f)

        # 尝试解密文件
        if reader.decrypt(password):
            logging.info(f"尝试解密[{filepath.name}文件]成功!")
        else:
            logging.error(f"尝试解密[{filepath.name}文件]失败, 密码不正确。")
            return filepath, None

        # 创建一个新的 PdfWriter 对象
        writer = pypdf.PdfWriter()

        # 将所有页面添加到新的 PdfWriter 对象中
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)

        # 将解密后的 PDF 写入输出文件
        outfile = filepath.with_suffix(".dec.pdf")
        with open(outfile, "wb") as _:
            writer.write(_)
            logging.info(f"写入解密文件到[{outfile}]")
            return filepath, outfile


def _is_encrypted(filepath: Path) -> bool:
    """判断文件是否加密"""
    return pypdf.PdfReader(filepath).is_encrypted


@cli.app.command("l", help="显示 pdf 文件列表, 别名: list")
@cli.app.command("list", help="显示 pdf 文件列表")
def list_dir() -> Tuple[List[Path], List[Path]]:
    """显示当前文件夹中的 pdf 文件列表

    Returns:
        Tuple[List[Path], List[Path]]: 返回未加密、已加密 pdf 文件清单
    """
    un_encrypted = list(_ for _ in CWD.rglob("*.pdf") if not _is_encrypted(_))
    encrypted = list(_ for _ in CWD.rglob("*.pdf") if _is_encrypted(_))

    logging.info(f"加密文件: [green bold]{encrypted}")
    logging.info(f"未加密文件: [green bold]{un_encrypted}")
    return un_encrypted, encrypted


@cli.app.command("d", help="解密文件, 别名: dec")
@cli.app.command("dec", help="解密文件")
def decrypt(
    password: str = Argument(help="解密密码"),
) -> None:
    """执行加密操作

    Args:
        password (str, optional): 解密密码
    """
    _, encrypted_files = list_dir()
    if not encrypted_files:
        logging.error(f"当前目录下没有已加密的 pdf: {CWD}")
        return

    dec_func = partial(decrypt_pdf, password=password)
    run_parallel(dec_func, encrypted_files)


@cli.app.command("e", help="加密文件, 别名: enc")
@cli.app.command("enc", help="加密文件")
def encrypt(
    password: str = Argument(help="加密密码"),
) -> None:
    un_encrypted, _ = list_dir()
    if not un_encrypted:
        logging.error(f"当前目录下没有未加密的 pdf: {CWD}")
        return

    enc_func = partial(encrypt_pdf, password=password)
    run_parallel(enc_func, un_encrypted)
