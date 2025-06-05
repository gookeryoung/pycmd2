"""功能: 将当前路径下所有图片合并为pdf文件."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PIL import Image

from pycmd2.common.cli import get_client

if TYPE_CHECKING:
    from pathlib import Path

cli = get_client(help_doc="图片转化 pdf 工具.")

images_converted: list[Image.Image] = []


def is_image_file(
    file_path: Path,
) -> bool:
    """验证文件是否为图片.

    Args:
        file_path (pathlib.Path): 文件路径

    Returns:
        bool: 是否为图片
    """
    try:
        with Image.open(file_path) as img:
            img.verify()  # 验证图像是否损坏
        return True
    except OSError:
        return False


def convert_image(
    filepath: Path,
) -> None:
    """合并所有图片为pdf.

    Args:
        filepath (Path): 图片文件路径
    """
    global images_converted

    img = Image.open(filepath)

    # 将图像转换为RGB格式
    img = img.convert("RGB")
    images_converted.append(img)


@cli.app.command()
def main() -> None:
    image_files = sorted(_ for _ in cli.cwd.iterdir() if is_image_file(_))
    if not image_files:
        logging.error(f"路径[{cli.cwd}]下未找到图片文件.")
        return

    cli.run(convert_image, image_files)

    if not images_converted:
        logging.error(f"[*] 路径[{cli.cwd}]下未找到图片文件.")
        return

    output_pdf = cli.cwd / f"{cli.cwd.name}.pdf"
    images_converted[0].save(
        output_pdf,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=images_converted[1:],
    )
    logging.info(f"[*] 创建PDF文件[{output_pdf.name}]成功!")
