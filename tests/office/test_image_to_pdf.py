from __future__ import annotations

import random
import shutil
import tempfile
from pathlib import Path
from typing import Callable
from typing import Generator
from typing import List
from typing import Tuple

import pytest
from PIL import Image
from pypdf import PdfReader
from typing_extensions import TypeAlias

from pycmd2.commands.office.image_to_pdf import ImageProcessor
from pycmd2.commands.office.image_to_pdf import main

ImageFunc: TypeAlias = Callable[[int, Tuple[int, int]], List[Image.Image]]


_FORMATS = [".png", ".jpg", ".jpeg"]


class TestImageProcessor:
    """Test for ImageProcessor."""

    @pytest.fixture(autouse=True, scope="session")
    def fixture_create_images(
        self,
        fixture_tmpdir: Path,
    ) -> None:
        """Get image file."""
        for format_ in _FORMATS:
            color = random.choice(["red", "green", "blue"])
            image = Image.new("RGB", (10, 10), color)
            image.save(fixture_tmpdir / f"test.{format_}")

    @pytest.fixture(scope="session")
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
            "pycmd2.commands.office.image_to_pdf.is_valid_image",
            lambda _: True,
        )

    def test_image_processor_with_no_images(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test ImageProcessor with no images."""
        processor = ImageProcessor(tmp_path)
        processor.convert_images()

        assert "No image file found in" in caplog.text

    def test_convert_failed(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fixture_tmpdir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test convert failed."""
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
        tmp_path: Path,
    ) -> None:
        """Test convert image."""
        image = Image.new("RGB", image_size, "red")
        image_path = tmp_path / "test.png"
        image.save(image_path)

        processor = ImageProcessor(tmp_path)
        processor.convert_images()

        w, h = processor.images[0].size
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
        tmp_path: Path,
    ) -> None:
        """Test convert image."""
        image = Image.new("RGB", image_size, "red")
        image_path = tmp_path / "test.png"
        image.save(image_path)

        processor = ImageProcessor(tmp_path)
        processor.convert_images(normalize=False)

        w, h = processor.images[0].size
        assert h <= w

    def test_main(
        self,
        fixture_tmpdir: Path,
    ) -> None:
        """Test main."""
        main(directory=fixture_tmpdir)

        output_pdf = fixture_tmpdir / f"{fixture_tmpdir.name}.pdf"
        assert output_pdf.exists()
        assert output_pdf.suffix == ".pdf"
        assert 0 < output_pdf.stat().st_size < 1024 * 1024

        with output_pdf.open("rb") as f:
            reader = PdfReader(f)
            assert len(reader.pages) == len(_FORMATS)

            for page in reader.pages:
                assert page.mediabox.width > 0
                assert page.mediabox.height > 0
