"""功能: 将当前路径下所有图片合并为pdf文件."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from typer import Argument
from typing_extensions import Annotated

from pycmd2.cli import get_client
from pycmd2.images.image_gray import is_valid_image

cli = get_client(help_doc="Convert images to pdf.")
logger = logging.getLogger(__name__)


@dataclass
class ImageProcessor:
    """图片处理类."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.converted_images: list[Image.Image] = []

    def _convert(
        self,
        filepath: Path,
    ) -> None:
        """Convert image to pdf.

        Args:
            filepath (Path): image file path
        """
        converted_image = Image.open(str(filepath)).convert("RGB")
        if converted_image:
            self.converted_images.append(converted_image)

    def convert_images(self) -> None:
        """Convert and merge all images into a single PDF file."""
        image_files = sorted(
            entry for entry in self.root_dir.iterdir() if is_valid_image(entry)
        )
        if not image_files:
            logger.error(f"No image file found in: {self.root_dir}")
            return

        cli.run(self._convert, image_files)

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
) -> None:
    proc = ImageProcessor(root_dir=directory)
    proc.convert_images()
