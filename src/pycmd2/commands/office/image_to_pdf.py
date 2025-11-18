"""功能: 将当前路径下所有图片合并为pdf文件.

命令: img2pdf [--normalize]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from PIL import Image
from PIL.Image import Resampling
from typer import Argument
from typer import Option
from typing_extensions import Annotated

from pycmd2.client import get_client
from pycmd2.commands.office.image_gray import is_valid_image
from pycmd2.config import TomlConfigMixin


class ImageToPdfConfig(TomlConfigMixin):
    """Configuration for image to pdf."""

    DPI: int = 300


cli = get_client(help_doc="Convert images to pdf.")
conf = ImageToPdfConfig()
logger = logging.getLogger(__name__)


@dataclass
class ImageProcessor:
    """Processor for image files."""

    __slots__ = "dpi", "images", "root_dir"

    def __init__(self, root_dir: Path, dpi: int = conf.DPI) -> None:
        self.root_dir = root_dir
        self.dpi = dpi
        self.images: list[Image.Image] = []

    @property
    def size(self) -> tuple[int, int]:
        """Get page size."""
        return (int(8.27 * self.dpi), int(11.69 * self.dpi))

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

        if normalize:
            image = self._auto_rotate_image(image)
            image = self._auto_scale_image(image)
            image.thumbnail(self.size, Resampling.LANCZOS)

            converted_image = Image.new(
                "RGB",
                self.size,
                (255, 255, 255),
            )
            converted_image.paste(
                image,
                (
                    (self.size[0] - image.size[0]) // 2,
                    (self.size[1] - image.size[1]) // 2,
                ),
            )
        else:
            converted_image = image

        if converted_image:
            logger.debug(f"Convert image: [u green]{filepath} successfully")
            self.images.append(converted_image.convert("RGB"))

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

    def _auto_scale_image(self, image: Image.Image) -> Image.Image:
        """自动缩放图片.

        Args:
            image: PIL Image对象

        Returns:
            缩放后的Image对象
        """
        if image.size[0] < self.size[0] or image.size[1] < self.size[1]:
            scale_w = self.size[0] / image.size[0]
            scale_h = self.size[1] / image.size[1]
            scale = max(
                scale_w,
                scale_h,
            )

            new_size = (
                int(image.size[0] * scale),
                int(image.size[1] * scale),
            )
            image = image.resize(new_size, Resampling.LANCZOS)
        return image

    def convert_images(self, *, normalize: bool = True) -> None:
        """Convert and merge all images into a single PDF file."""
        logger.info(f"Start converting, using dpi={self.dpi}")

        image_files = sorted(entry for entry in self.root_dir.iterdir() if is_valid_image(entry))
        if not image_files:
            logger.error(f"No image file found in: {self.root_dir}")
            return

        cli.run(partial(self._convert, normalize=normalize), image_files)

        if not self.images:
            logger.error(f"No converted image file found in: {self.root_dir}")
            return

        self.save_pdf()

    def save_pdf(self) -> None:
        """Save converted images to a single PDF file."""
        output_pdf = self.root_dir / f"{self.root_dir.name}.pdf"
        self.images[0].save(
            output_pdf,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=self.images[1:],
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
    dpi: Annotated[
        int,
        Option(
            "--dpi",
            help="图片分辨率",
        ),
    ] = conf.DPI,
) -> None:
    proc = ImageProcessor(root_dir=directory, dpi=dpi)
    proc.convert_images(normalize=normalize)
