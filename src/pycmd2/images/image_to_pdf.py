"""功能: 将当前路径下所有图片合并为pdf文件."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image
from typer import Argument
from typing_extensions import Annotated

from pycmd2.common.cli import get_client

from .image_gray import is_valid_image

if TYPE_CHECKING:
    from pathlib import Path

cli = get_client(help_doc="图片转化 pdf 工具.")
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
        """合并所有图片为pdf.

        Args:
            filepath (Path): 图片文件路径
        """
        converted_image = Image.open(str(filepath)).convert("RGB")
        self.converted_images.append(converted_image)

    def convert_images(self) -> None:
        """合并所有图片为pdf."""
        image_files = sorted(
            _ for _ in self.root_dir.iterdir() if is_valid_image(_)
        )
        if not image_files:
            logger.error(f"路径[{self.root_dir}]下未找到图片文件.")
            return

        cli.run(self._convert, image_files)

        if not self.converted_images:
            logger.error(f"[*] 路径[{self.root_dir}]下未找到图片文件.")
            return

        output_pdf = self.root_dir / f"{self.root_dir.name}.pdf"
        self.converted_images[0].save(
            output_pdf,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=self.converted_images[1:],
        )
        logger.info(f"[*] 创建PDF文件[{output_pdf.name}]成功!")


@cli.app.command()
def main(
    directory: Annotated[
        Path,
        Argument(help="图片文件夹路径"),
    ] = cli.cwd,
) -> None:
    proc = ImageProcessor(root_dir=directory)
    proc.convert_images()
