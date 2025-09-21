"""功能: 将当前路径下所有图片合并为pdf文件."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from PIL import Image
from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin
from pycmd2.images.image_gray import is_valid_image


class ImageToPdfConfig(TomlConfigMixin):
    """Configuration for image to pdf."""

    DPI: int = 120
    PAGE_SIZE: tuple[int, int] = (int(8.27 * DPI), int(11.69 * DPI))


cli = get_client(help_doc="Convert images to pdf.")
conf = ImageToPdfConfig()
logger = logging.getLogger(__name__)


@dataclass
class ImageProcessor:
    """Processor for image files."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.converted_images: list[Image.Image] = []

    def _convert(
        self,
        filepath: Path,
        *,
        normalize: bool = True,
    ) -> None:
        """Convert image to pdf.

        Args:
            filepath (Path): image file path
            normalize (bool, optional): normalize image. Defaults to True.
        """
        image = Image.open(str(filepath))

        # Rotate image if it is landscape
        image = self._auto_rotate_image(image)

        if normalize:
            image.thumbnail(conf.PAGE_SIZE, Image.LANCZOS)  # type: ignore  # noqa: PGH003
            converted_image = Image.new(
                "RGB",
                conf.PAGE_SIZE,
                (255, 255, 255),
            )
            converted_image.paste(
                image,
                (
                    (conf.PAGE_SIZE[0] - image.size[0]) // 2,
                    (conf.PAGE_SIZE[1] - image.size[1]) // 2,
                ),
            )
        else:
            converted_image = image

        if image:
            self.converted_images.append(converted_image.convert("RGB"))

    def _auto_rotate_image(self, image: Image.Image) -> Image.Image:
        """自动旋转图片以校正方向.

        Args:
            image: PIL Image对象

        Returns:
            旋转后的Image对象
        """
        width, height = image.size
        if width > height:
            image = image.rotate(90, expand=True)
        return image

    def convert_images(self, *, normalize: bool) -> None:
        """Convert and merge all images into a single PDF file."""
        image_files = sorted(
            entry for entry in self.root_dir.iterdir() if is_valid_image(entry)
        )
        if not image_files:
            logger.error(f"No image file found in: {self.root_dir}")
            return

        cli.run(partial(self._convert, normalize=normalize), image_files)

        if not self.converted_images:
            logger.error(f"No converted image file found in: {self.root_dir}")
            return

        output_pdf = self.root_dir / f"{self.root_dir.name}.pdf"
        self.converted_images[0].save(
            output_pdf,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=self.converted_images[1:],
        )
        logger.info(f"Create pdf file: [u green]{output_pdf}")


@cli.app.command()
def main(
    directory: Annotated[
        Path,
        Argument(help="图片文件夹路径"),
    ] = cli.cwd,
    *,
    normalize: Annotated[
        bool,
        Option(
            "--normalize",
            help="是否进行图片尺寸归一化处理",
        ),
    ] = True,
) -> None:
    proc = ImageProcessor(root_dir=directory)
    proc.convert_images(normalize=normalize)
