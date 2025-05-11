"""
功能: 将指定图像转为灰度图
命令: imgr.exe [-b?] -w [width?] -d [directory?]
"""

import logging
import os
import pathlib
from functools import partial
from pathlib import Path

from PIL import Image
from typer import Argument
from typer import Option

from pycmd2.common.cli import get_client

cli = get_client(help="图片转换工具.")


def is_valid_image(file_path: Path):
    """
    综合校验文件是否为有效图片（支持 JPEG/PNG/GIF/BMP 等常见格式）
    返回：布尔值，True 表示有效图片文件
    """
    # 基础校验：文件存在性及大小
    if not os.path.exists(file_path):
        return False
    if os.path.getsize(file_path) == 0:
        return False

    # 第一层：扩展名校验（快速过滤）
    img_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in img_exts:
        return False

    # 第二层：文件头校验（魔数校验）
    magic_numbers = {
        b"\xff\xd8\xff": "jpeg",  # JPEG
        b"\x89PNG\r\n\x1a\n": "png",
        b"GIF87a": "gif",
        b"GIF89a": "gif",
        b"BM": "bmp",
        b"RIFF....WEBP": "webp",  # 实际需更精确判断
    }
    try:
        with open(file_path, "rb") as f:
            header = f.read(12)
            if not any(header.startswith(k) for k in magic_numbers):
                return False
    except OSError:
        return False

    # 第三层：图像完整性验证
    try:
        with Image.open(file_path) as img:
            img.verify()
            if img.format and img.format.lower() not in [
                v for v in magic_numbers.values()
            ]:
                return False
    except (OSError, SyntaxError, ValueError):
        return False

    return True


def convert_img(img_path: pathlib.Path, black_mode: bool, width: int):
    """转化图片

    :param img_path: 待处理图片路径
    :param black_mode: 黑白模式
    :param width: 缩放尺寸宽度
    """
    if not img_path.exists():
        raise FileNotFoundError(img_path)

    print(f"[*] 开始转换图片[{img_path.name}]")
    img = Image.open(img_path.as_posix())
    img_conv = img.convert("L")

    if black_mode:
        img_conv = img_conv.point(lambda x: 0 if x < 128 else 255, "1")

    if width:
        new_height = int(width / img_conv.width * img_conv.height)
        img_conv = img_conv.resize((width, new_height), resample=Image.LANCZOS)

    new_img_path = img_path.with_name(img_path.stem + "_conv.png")
    img_conv.save(new_img_path, optimize=True, quality=90)
    print(f"[*] 转换图片[{img_path.name}]->[{new_img_path.name}]")


@cli.app.command()
def main(
    width: int = Argument(None, help="缩放尺寸宽度"),
    black: bool = Option(False, help="黑白模式"),
):
    image_files = list(
        _ for _ in pathlib.Path(cli.CWD).glob("*.*") if is_valid_image(_)
    )
    if not len(image_files):
        logging.error("未找到待处理图片文件")
        return

    conver_func = partial(convert_img, black_mode=black, width=width)
    cli.run(conver_func, image_files)
