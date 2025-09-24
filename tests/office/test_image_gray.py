from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import NoReturn

import pytest
from PIL import Image

from pycmd2.office.image_gray import convert_img
from pycmd2.office.image_gray import is_valid_image


class _WriteType(Enum):
    """Write file type, only for testing purposes."""

    NO_CREATE = 0
    TOUCH = 1
    WRITE_CONTENT = 2


_CREATE_FORMATS: list[str] = [
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tiff",
    "webp",
    "gif",
]


class TestImageGray:
    """Test for image_gray module."""

    def _is_valid_image(self, filepath: Path) -> bool:
        return filepath.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".webp",
            ".gif",
        }

    @pytest.fixture(scope="session")
    def fixture_img_dir(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        """Fixture for temporary directory.

        Returns:
            Path: Temporary directory path.
        """
        return tmp_path_factory.mktemp("test_image_gray")

    @pytest.fixture(autouse=True, scope="session")
    def fixture_create_images(self, fixture_img_dir: Path) -> None:
        """Create image files."""
        for format_ in _CREATE_FORMATS:
            image = Image.new("RGB", (100, 100), color="red")
            imagepath = fixture_img_dir / f"test.{format_}"
            image.save(imagepath)
            image.close()

    @pytest.fixture(autouse=True)
    def mock_is_valid_image(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Mock is_valid_image."""
        monkeypatch.setattr(
            "pycmd2.office.image_gray.is_valid_image",
            self._is_valid_image,
        )

    @pytest.mark.parametrize(
        ("filename", "write_type"),
        [
            ("test.txt", _WriteType.WRITE_CONTENT),
            ("test.png", _WriteType.WRITE_CONTENT),
            ("non_existent.png", _WriteType.NO_CREATE),
            ("empty.jpg", _WriteType.TOUCH),
        ],
    )
    def test_is_valid_image_with_invalid_files(
        self,
        filename: str,
        *,
        write_type: _WriteType,
        tmp_path: Path,
    ) -> None:
        """Test is_valid_image with invalid files."""
        img_path = tmp_path / filename

        if write_type == _WriteType.WRITE_CONTENT:
            img_path.write_text("invalid content")
        elif write_type == _WriteType.TOUCH:
            img_path.touch()
        elif write_type == _WriteType.NO_CREATE:
            pass

        assert is_valid_image(img_path) is False

    @pytest.mark.parametrize("format_", _CREATE_FORMATS)
    def test_is_valid_image_with_valid_files(
        self,
        format_: str,
        fixture_img_dir: Path,
    ) -> None:
        """Test is_valid_image with valid image files."""
        assert is_valid_image(fixture_img_dir / f"test.{format_}") is True

    def test_is_valid_image_with_file_open_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fixture_img_dir: Path,
    ) -> None:
        """Test is_valid_image with OSError."""

        def mock_open(*args: object, **kwargs: object) -> NoReturn:  # noqa: ARG001
            raise OSError

        monkeypatch.setattr("pathlib.Path.open", mock_open)

        assert is_valid_image(fixture_img_dir / "test.png") is False

    def test_is_valid_image_with_image_open_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fixture_img_dir: Path,
    ) -> None:
        """Test is_valid_image with SyntaxError."""

        def mock_open(*args: object, **kwargs: object) -> NoReturn:  # noqa: ARG001
            raise OSError

        monkeypatch.setattr("PIL.Image.open", mock_open)

        assert is_valid_image(fixture_img_dir / "test.png") is False

    @pytest.mark.parametrize("format_", _CREATE_FORMATS)
    def test_convert_img_with_valid_images_real(
        self,
        format_: str,
        fixture_img_dir: Path,
    ) -> None:
        """Test convert_img with valid images."""
        img_path = fixture_img_dir / f"test.{format_}"

        # Test color mode
        convert_img(img_path, black_mode=False, width=0)
        converted_path = img_path.with_name(img_path.stem + "_conv.png")
        assert converted_path.exists()
        assert converted_path.suffix == ".png"
        assert converted_path.stat().st_size > 0

        # Test black & white mode
        convert_img(img_path, black_mode=True, width=0)
        bw_path = img_path.with_name(img_path.stem + "_conv.png")
        assert bw_path.exists()
        assert bw_path.suffix == ".png"
        assert bw_path.stat().st_size > 0

        # Test width
        convert_img(img_path, black_mode=False, width=100)
        converted_path = img_path.with_name(img_path.stem + "_conv.png")
        assert converted_path.exists()
        assert converted_path.suffix == ".png"
        assert converted_path.stat().st_size > 0
        with Image.open(converted_path) as img:
            assert img.size[0] == 100  # noqa: PLR2004

    def test_convert_img_not_found(
        self,
        fixture_img_dir: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test convert_img with non-existent file."""
        non_existent_file = fixture_img_dir / "non_existent.jpg"
        convert_img(non_existent_file, black_mode=False, width=0)

        assert f"File not found: {non_existent_file}" in caplog.text
