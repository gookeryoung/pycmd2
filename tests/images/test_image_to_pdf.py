from __future__ import annotations

import random
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Callable
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from PIL import Image

from pycmd2.images.image_to_pdf import ImageProcessor


class TestImageProcessor:
    """Test for ImageProcessor."""

    def _is_valid_image(self, filepath: Path) -> bool:
        return filepath.suffix.lower() in {".png", ".jpg", ".jpeg"}

    @pytest.fixture
    def fixture_create_images(
        self,
        fixture_tmpdir: Path,
    ) -> Callable[[int], list[Image.Image]]:
        """Get image file.

        Returns:
            list[Image.Image]: image list
        """

        def get_image(count: int) -> list[Image.Image]:
            images = []
            for _ in range(count):
                color = random.choice(["red", "green", "blue"])
                suffix = random.choice(["png", "jpg", "jpeg"])
                image = Image.new("RGB", (100, 100), color=color)
                imagepath = fixture_tmpdir / f"test{uuid.uuid4()}.{suffix}"
                image.save(imagepath)
                images.append(image)
            return images

        return get_image

    @pytest.fixture
    def fixture_tmpdir(self) -> Generator[Path, None, None]:
        """Fixture for temporary directory.

        Yields:
            Generator[Path, None, None]: The temporary directory.
        """
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.mark.parametrize("filecount", [1, 3, 6])
    @patch("pycmd2.images.image_gray.is_valid_image")
    def test_image_processor_with_valid_images(
        self,
        mock_is_valid_image: MagicMock,
        filecount: int,
        fixture_create_images: Callable[[int], list[Image.Image]],
        fixture_tmpdir: Path,
    ) -> None:
        """Test ImageProcessor with valid images."""
        fixture_create_images(filecount)

        mock_is_valid_image.side_effect = self._is_valid_image

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert len(processor.converted_images) == filecount

        output_pdf = fixture_tmpdir / f"{fixture_tmpdir.name}.pdf"
        assert output_pdf.exists()
        assert output_pdf.suffix == ".pdf"

    @patch("pycmd2.images.image_to_pdf.is_valid_image", return_value=True)
    def test_image_processor_with_no_images(
        self,
        fixture_tmpdir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test ImageProcessor with no images."""
        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert "No image file found in" in caplog.text

    @patch("pycmd2.images.image_to_pdf.is_valid_image")
    @patch("PIL.Image.open")
    def test_convert_failed(
        self,
        mock_image_open: MagicMock,
        mock_is_valid_image: MagicMock,
        fixture_create_images: Callable[[int], list[Image.Image]],
        fixture_tmpdir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test convert failed."""
        fixture_create_images(1)

        mock_is_valid_image.return_value = True
        mock_image_open.side_effect = lambda _: None

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert "No converted image file found in" in caplog.text

    @patch("pycmd2.images.image_to_pdf.is_valid_image")
    def test_main_function(
        self,
        mock_is_valid_image: MagicMock,
        fixture_tmpdir: Path,
        fixture_create_images: Callable[[int], list[Image.Image]],
    ) -> None:
        """Test main function."""
        fixture_create_images(1)

        mock_is_valid_image.side_effect = self._is_valid_image

        proc = ImageProcessor(fixture_tmpdir)
        proc.convert_images()

        output_pdf = fixture_tmpdir / f"{fixture_tmpdir.name}.pdf"
        assert output_pdf.exists()
        assert output_pdf.suffix == ".pdf"

    @patch("pycmd2.images.image_to_pdf.is_valid_image")
    def test_is_valid_image_check(self, mock_is_valid_image: MagicMock) -> None:
        """Test is_valid_image check."""
        mock_is_valid_image.side_effect = self._is_valid_image

        assert mock_is_valid_image(Path("test.jpg"))
        assert mock_is_valid_image(Path("test.png"))
        assert mock_is_valid_image(Path("test.jpeg"))
        assert not mock_is_valid_image(Path("test.txt"))
