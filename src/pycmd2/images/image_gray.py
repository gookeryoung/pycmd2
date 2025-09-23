"""功能: 将指定图像转为灰度图.

命令: imgr [-b?] -w [width?] -d [directory?]
"""

from __future__ import annotations

import logging
import pathlib
from functools import partial
from pathlib import Path
from typing import ClassVar

from PIL import Image
from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class ImageGrayConfig(TomlConfigMixin):
    """ImageToGray config."""

    GRAYSCALE_THRESHOLD: int = 128
    EXTENSIONS: ClassVar[list[str]] = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
    ]


cli = get_client(help_doc="Convert image to grayscale.")
conf = ImageGrayConfig()
logger = logging.getLogger(__name__)

# Magic numbers for image file header.
_MAGIC_NUMBERS: dict[str, bytes] = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "gif": b"GIF87a",
    "bmp": b"BM",
    "webp": b"RIFFf\x00\x00\x00WEBP",
    "tiff": b"II*\x00",
    "ico": b"ICON",
    "svg": b"<svg",
}


def is_valid_image(file_path: Path) -> bool:  # noqa: PLR0911
    """Validate image file.

    Arguments:
        file_path: image file path

    Returns:
        bool: if the file is valid image file
    """
    # Basic validation.
    if not file_path.exists():
        return False
    if file_path.stat().st_size == 0:
        return False

    # Extension validation.
    ext = file_path.suffix.lower()
    if ext not in set(conf.EXTENSIONS):
        return False

    # File header validation.
    try:
        with file_path.open("rb") as f:
            header = f.read(12)
            if not any(header.startswith(k) for k in _MAGIC_NUMBERS.values()):
                return False
    except OSError:
        return False

    # Image format validation.
    try:
        with Image.open(file_path) as img:
            img.verify()
            if img.format and img.format.lower() not in list(
                _MAGIC_NUMBERS.keys(),
            ):
                return False
    except (OSError, SyntaxError, ValueError):
        return False

    return True


def convert_img(
    img_path: pathlib.Path,
    *,
    black_mode: bool,
    width: int,
) -> None:
    """转化图片.

    Args:
        img_path: 待处理图片路径
        black_mode: 黑白模式
        width: 缩放尺寸宽度
    """
    if not img_path.exists():
        logger.warning(f"File not found: {img_path}")
        return

    logger.info(f"Start converting: [u]{img_path.name}")
    with Image.open(img_path.as_posix()) as img:
        img_conv = img.convert("L")

        if black_mode:
            img_conv = img_conv.point(
                lambda x: 0 if x < conf.GRAYSCALE_THRESHOLD else 255,
                "1",
            )

        if width:
            new_height = int(width / img_conv.width * img_conv.height)
            img_conv = img_conv.resize(
                (width, new_height),
                resample=Image.LANCZOS,  # type: ignore  # noqa: PGH003
            )

        new_img_path = img_path.with_name(img_path.stem + "_conv.png")
        img_conv.save(new_img_path, optimize=True, quality=90)

    logger.info(f"Contert finished: {img_path.name}->{new_img_path.name}")


@cli.app.command()
def main(
    width: Annotated[int, Argument(help="缩放尺寸宽度")] = 0,
    *,
    black: Annotated[bool, Option(help="黑白模式")] = False,
) -> None:
    image_files = [
        f
        for f in pathlib.Path(cli.cwd).glob("*.*")
        if is_valid_image(f) and not f.stem.endswith("_conv")
    ]
    if not image_files:
        logger.error(f"No image file found in current directory: {cli.cwd}.")
        return

    logger.info(
        f"Found {len(image_files)} image files"
        f": {[f.name for f in image_files]}",
    )
    conver_func = partial(convert_img, black_mode=black, width=width)
    cli.run(conver_func, image_files)
