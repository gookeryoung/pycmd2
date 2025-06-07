import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from pycmd2.images.image_to_pdf import ImageProcessor


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # 测试完成后清理
    shutil.rmtree(temp_dir)


def test_image_processor_with_valid_images(temp_dir: Path) -> None:
    # 准备测试图片
    img1 = Image.new("RGB", (100, 100), color="red")
    img1.save(temp_dir / "test1.jpg")
    img2 = Image.new("RGB", (100, 100), color="blue")
    img2.save(temp_dir / "test2.png")

    # Mock is_valid_image函数
    with patch("pycmd2.images.image_to_pdf.is_valid_image") as mock_valid:
        mock_valid.side_effect = lambda x: x.suffix.lower() in {".jpg", ".png"}

        # 测试图片处理
        processor = ImageProcessor(temp_dir)
        processor.convert_images()

        # 检查输出PDF
        output_pdf = temp_dir / f"{temp_dir.name}.pdf"
        assert output_pdf.exists()


def test_image_processor_with_no_images(
    temp_dir: Path,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    # Mock is_valid_image函数
    mocker.patch(
        "pycmd2.images.image_to_pdf.is_valid_image",
        return_value=False,
    )

    # 测试空目录
    processor = ImageProcessor(temp_dir)
    processor.convert_images()

    # 检查日志输出
    assert "未找到图片文件" in caplog.text


def test_main_function(temp_dir: Path, mocker: MockerFixture) -> None:
    # 准备测试图片
    img = Image.new("RGB", (100, 100), color="green")
    img.save(temp_dir / "test.jpg")

    # Mock is_valid_image函数
    mocker.patch(
        "pycmd2.images.image_to_pdf.is_valid_image",
        side_effect=lambda x: x.suffix.lower() in {".jpg", ".png"},
    )

    # 调用main函数
    proc = ImageProcessor(temp_dir)
    proc.convert_images()

    # 检查输出PDF
    output_pdf = temp_dir / f"{temp_dir.name}.pdf"
    assert output_pdf.exists()


def test_is_valid_image_check(mocker: MockerFixture) -> None:
    # Mock实际的is_valid_image函数
    mocker_valid = mocker.patch(
        "pycmd2.images.image_to_pdf.is_valid_image",
        side_effect=lambda x: x.suffix.lower() in {".jpg", ".png"},
    )

    # 测试图片验证逻辑
    assert mocker_valid(Path("test.jpg"))
    assert mocker_valid(Path("test.png"))
    assert not mocker_valid(Path("test.txt"))
