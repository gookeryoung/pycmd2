from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any
from typing import Callable
from typing import List
from typing import NoReturn
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fpdf import FPDF

from src.pycmd2.commands.office.pdf_crypt import decrypt
from src.pycmd2.commands.office.pdf_crypt import decrypt_pdf
from src.pycmd2.commands.office.pdf_crypt import encrypt
from src.pycmd2.commands.office.pdf_crypt import encrypt_pdf
from src.pycmd2.commands.office.pdf_crypt import is_encrypted
from src.pycmd2.commands.office.pdf_crypt import list_pdf


@pytest.fixture
def simple_pdf(tmp_path: Path) -> Path:
    """创建一个简单的未加密PDF文件用于测试.

    Returns:
        Path: 简单PDF文件路径
    """
    pdf_path = tmp_path / "test.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Test PDF content", ln=True)
    pdf.output(str(pdf_path))
    return pdf_path


@pytest.fixture
def encrypted_pdf(simple_pdf: Path) -> Path | None:
    """创建一个加密的PDF文件用于测试.

    Args:
        simple_pdf (Path): 简单PDF文件路径

    Returns:
        Path | None: 加密PDF文件路径
    """
    _, encrypted_path = encrypt_pdf(simple_pdf, "password123")
    return encrypted_path


class TestPdfCryptFunctions:
    """测试PDF加解密功能函数."""

    def test_is_encrypted_with_unencrypted_pdf(self, simple_pdf: Path) -> None:
        """测试未加密PDF的检测."""
        assert not is_encrypted(simple_pdf)

    def test_is_encrypted_with_encrypted_pdf(self, encrypted_pdf: Path) -> None:
        """测试加密PDF的检测."""
        assert is_encrypted(encrypted_pdf)

    def test_encrypt_pdf_success(self, simple_pdf: Path) -> None:
        """测试PDF加密功能."""
        original_path, encrypted_path = encrypt_pdf(simple_pdf, "password123")

        assert original_path == simple_pdf
        assert encrypted_path is not None
        assert encrypted_path.suffixes == [".enc", ".pdf"]
        assert encrypted_path.exists()
        assert is_encrypted(encrypted_path)

    def test_encrypt_pdf_failure(
        self,
        simple_pdf: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试PDF加密失败的情况."""

        # 模拟写入失败
        def mock_open(*args, **kwargs) -> NoReturn:  # noqa: ANN002, ANN003, ARG001
            msg = "Permission denied"
            raise OSError(msg)

        monkeypatch.setattr(Path, "open", mock_open)
        original_path, encrypted_path = encrypt_pdf(simple_pdf, "password123")

        assert original_path == simple_pdf
        assert encrypted_path is None

    def test_decrypt_pdf_success(self, encrypted_pdf: Path) -> None:
        """测试PDF解密功能."""
        if encrypted_pdf is None:
            pytest.fail("加密PDF文件创建失败")

        original_path, decrypted_path = decrypt_pdf(
            encrypted_pdf,
            "password123",
        )

        assert original_path == encrypted_pdf
        assert decrypted_path is not None
        assert decrypted_path.suffix == ".pdf"
        assert decrypted_path.exists()
        assert not is_encrypted(decrypted_path)

    def test_decrypt_pdf_failure_wrong_password(
        self,
        encrypted_pdf: Path,
    ) -> None:
        """测试使用错误密码解密PDF."""
        if encrypted_pdf is None:
            pytest.fail("加密PDF文件创建失败")

        original_path, decrypted_path = decrypt_pdf(
            encrypted_pdf,
            "wrongpassword",
        )

        assert original_path == encrypted_pdf
        assert decrypted_path is None

    def test_list_pdf(
        self,
        tmp_path: Path,
        simple_pdf: Path,
        encrypted_pdf: Path | None,
    ) -> None:
        """测试列出PDF文件功能."""
        if encrypted_pdf is None:
            pytest.fail("加密PDF文件创建失败")

        # 模拟当前工作目录
        mock_cli = MagicMock()
        mock_cli.cwd = tmp_path

        with patch("src.pycmd2.commands.office.pdf_crypt.cli", mock_cli):
            unencrypted, encrypted = list_pdf()

            assert len(unencrypted) == 1
            assert len(encrypted) == 1
            assert simple_pdf in unencrypted
            assert encrypted_pdf in encrypted


class TestPdfCryptCommands:
    """测试PDF加解密命令行接口."""

    def test_encrypt_command_no_files(
        self,
        caplog: pytest.LogCaptureFixture,
        tmp_path: Path,
    ) -> None:
        """测试当没有未加密文件时的加密命令."""
        # 创建一个空目录
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # 模拟当前工作目录
        mock_cli = MagicMock()
        mock_cli.cwd = empty_dir

        with patch("src.pycmd2.commands.office.pdf_crypt.cli", mock_cli):
            with caplog.at_level(logging.ERROR):
                encrypt("password123")

            assert f"当前目录下没有未加密的 pdf: {empty_dir}" in caplog.text

    def test_encrypt_command_success(
        self,
        tmp_path: Path,
        simple_pdf: Path,  # noqa: ARG002
    ) -> None:
        """测试加密命令成功执行."""
        mock_cli = MagicMock()
        mock_cli.cwd = tmp_path

        # 模拟cli.run方法
        def mock_run(func: Callable[..., Any], files: List[Path]) -> None:
            for f in files:
                func(f)

        mock_cli.run = mock_run

        with patch("src.pycmd2.commands.office.pdf_crypt.cli", mock_cli):
            encrypt("password123")

            encrypted_file = tmp_path / "test.enc.pdf"
            assert encrypted_file.exists()
            assert is_encrypted(encrypted_file)

    def test_decrypt_command_no_files(
        self,
        caplog: pytest.LogCaptureFixture,
        tmp_path: Path,
        simple_pdf: Path,
    ) -> None:
        """测试当没有加密文件时的解密命令."""
        # 创建一个只包含未加密PDF的目录
        plain_dir = tmp_path / "plain"
        plain_dir.mkdir()
        plain_pdf = plain_dir / "plain.pdf"
        shutil.copy(str(simple_pdf), plain_pdf)

        # 模拟当前工作目录
        mock_cli = MagicMock()
        mock_cli.cwd = plain_dir

        with patch("src.pycmd2.commands.office.pdf_crypt.cli", mock_cli):
            with caplog.at_level(logging.ERROR):
                decrypt("password123")

            assert f"当前目录下没有已加密的 pdf: {plain_dir}" in caplog.text

    def test_decrypt_command_success(
        self,
        tmp_path: Path,
        encrypted_pdf: Path | None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """测试解密命令成功执行."""
        if encrypted_pdf is None:
            pytest.fail("加密PDF文件创建失败")

        # 模拟cli.run方法
        def mock_run(func: Callable[..., Any], files: List[Path]) -> None:
            for f in files:
                func(f)

        mock_cli = MagicMock()
        mock_cli.cwd = tmp_path
        mock_cli.run = mock_run

        monkeypatch.setattr("pycmd2.commands.office.pdf_crypt.cli", mock_cli)

        decrypt("password123")

        decrypted_file = tmp_path / "test.pdf"
        assert decrypted_file.exists()
        assert not is_encrypted(decrypted_file)
