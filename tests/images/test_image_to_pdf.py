from __future__ import annotations

import random
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Callable
from typing import Generator
from typing import List
from typing import Tuple

import pytest
from PIL import Image
from pypdf import PdfReader
from typing_extensions import TypeAlias

from pycmd2.images.image_to_pdf import ImageProcessor

ImageFunc: TypeAlias = Callable[[int, Tuple[int, int]], List[Image.Image]]


class TestImageProcessor:
    """Test for ImageProcessor."""

    def _is_valid_image(self, filepath: Path) -> bool:
        return filepath.suffix.lower() in {".png", ".jpg", ".jpeg"}

    @pytest.fixture
    def fixture_create_images(
        self,
        fixture_tmpdir: Path,
    ) -> ImageFunc:
        """Get image file.

        Returns:
            list[Image.Image]: image list
        """

        def get_image(
            count: int,
            size: tuple[int, int] = (100, 100),
        ) -> List[Image.Image]:
            images = []
            for _ in range(count):
                color = random.choice(["red", "green", "blue"])
                suffix = random.choice(["png", "jpg", "jpeg"])
                image = Image.new("RGB", size, color=color)
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

    @pytest.fixture(autouse=True)
    def mock_is_valid_image(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Mock is_valid_image."""
        monkeypatch.setattr(
            "pycmd2.images.image_to_pdf.is_valid_image",
            self._is_valid_image,
        )

    @pytest.mark.parametrize("filecount", [1, 3])
    def test_image_processor_with_valid_images(
        self,
        filecount: int,
        fixture_create_images: ImageFunc,
        fixture_tmpdir: Path,
    ) -> None:
        """Test ImageProcessor with valid images."""
        fixture_create_images(filecount, (100, 100))

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert len(processor.converted_images) == filecount

        output_pdf = fixture_tmpdir / f"{fixture_tmpdir.name}.pdf"
        assert output_pdf.exists()
        assert output_pdf.suffix == ".pdf"
        assert 0 < output_pdf.stat().st_size < 1024 * 1024

        with output_pdf.open("rb") as f:
            reader = PdfReader(f)
            assert len(reader.pages) == filecount

    def test_image_processor_with_no_images(
        self,
        fixture_tmpdir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test ImageProcessor with no images."""
        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert "No image file found in" in caplog.text

    def test_convert_failed(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fixture_create_images: ImageFunc,
        fixture_tmpdir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test convert failed."""
        fixture_create_images(1, (100, 100))

        monkeypatch.setattr("PIL.Image.open", lambda _: None)

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        assert "No converted image file found in" in caplog.text

    @pytest.mark.parametrize(
        "image_size",
        [
            (100, 100),
            (200, 100),
            (100, 200),
            (300, 300),
        ],
    )
    def test_convert_image(
        self,
        image_size: tuple[int, int],
        fixture_tmpdir: Path,
        fixture_create_images: ImageFunc,
    ) -> None:
        """Test convert image."""
        fixture_create_images(1, image_size)

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images()

        w, h = processor.converted_images[0].size
        assert h >= w

    @pytest.mark.parametrize(
        "image_size",
        [
            (200, 100),
            (300, 200),
        ],
    )
    def test_convert_image_not_normalized(
        self,
        image_size: tuple[int, int],
        fixture_tmpdir: Path,
        fixture_create_images: ImageFunc,
    ) -> None:
        """Test convert image."""
        fixture_create_images(1, image_size)

        processor = ImageProcessor(fixture_tmpdir)
        processor.convert_images(normalize=False)

        w, h = processor.converted_images[0].size
        assert h <= w
