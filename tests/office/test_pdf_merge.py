from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from typing import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fpdf import FPDF

from src.pycmd2.office.pdf_merge import main
from src.pycmd2.office.pdf_merge import PdfFileInfo
from src.pycmd2.office.pdf_merge import search_directory


@pytest.fixture
def mock_cli() -> Generator[MagicMock]:
    with patch("src.pycmd2.office.pdf_merge.cli") as mock:
        mock.cwd = Path("test_dir")
        mock.logger.error.return_value = None
        mock.logger.info.return_value = None
        yield mock


@dataclass
class PDFTestFile:
    """PDF test file."""

    filepath: Path
    text: str


_PDF_FILES: list[PDFTestFile] = [
    PDFTestFile(filepath=Path("file1.pdf"), text="First level PDF 1"),
    PDFTestFile(filepath=Path("file2.pdf"), text="First level PDF 2"),
    PDFTestFile(filepath=Path("subdir") / "file3.pdf", text="Second level PDF"),
]


class TestPDFMerge:
    """PDF 合并测试."""

    def _create_pdf(self, filepath: Path, text: str) -> None:
        if not (filepath.parent).exists():
            (filepath.parent).mkdir(parents=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=text, ln=True)  # type: ignore
        pdf.output(str(filepath))

    @pytest.fixture(scope="session")
    def test_dir(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        """Test directory path.

        Returns:
            Path: Test directory path.
        """
        return tmp_path_factory.mktemp("test_pdf_merge")

    @pytest.fixture(scope="session", autouse=True)
    def generate_pdf_files(self, test_dir: Path) -> None:
        """Generate test PDF files for merging."""
        for file in _PDF_FILES:
            self._create_pdf(test_dir / file.filepath, file.text)

    def test_pdf_file_info(self) -> None:
        """测试 PdfFileInfo 类的基本功能."""
        pdf_info = PdfFileInfo(
            prefix="test",
            files=[f.filepath for f in _PDF_FILES],
            children=[],
        )
        assert pdf_info.prefix == "test"
        assert len(pdf_info.files) == len(_PDF_FILES)
        assert pdf_info.count() == len(_PDF_FILES)
        assert "file1.pdf" in str(pdf_info)

    def test_search_directory(self, test_dir: Path) -> None:
        """测试 search_directory 函数."""
        pdf_info = search_directory(test_dir, test_dir)

        assert pdf_info is not None
        assert len(pdf_info.files) == 2  # noqa: PLR2004
        assert len(pdf_info.children) == 1  # subdir

        # Check subdir content
        subdir_info = pdf_info.children[0]
        assert subdir_info.prefix == "subdir"
        assert len(subdir_info.files) == 1  # file3.pdf

    def test_main_with_no_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test main function with no files."""
        monkeypatch.chdir(tmp_path)

        main()

        assert "PDF files not found, exit" in caplog.text

    def test_merge_file_info(self, mock_cli: MagicMock, tmp_path: Path) -> None:
        """测试 PdfFileInfo.merge_file_info 方法."""
        pdf_info = PdfFileInfo(
            prefix="test",
            files=[tmp_path / "file1.pdf", tmp_path / "file2.pdf"],
            children=[],
        )

        # Create valid PDF files for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 10 >>\nstream\nBT /F1 12 Tf 72 720 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000257 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n360\n%%EOF"  # noqa: E501
        for f in pdf_info.files:
            f.write_bytes(pdf_content)

        mock_writer = MagicMock()
        mock_writer.add_outline_item.return_value = "bookmark"

        # Mock the cli.run method
        def mock_run(func: Callable[[Path], None], files: list[Path]) -> None:
            for f in files:
                func(f)

        with patch("src.pycmd2.office.pdf_merge.cli.run", mock_run):
            mock_cli.cwd = tmp_path
            pdf_info.merge_file_info(pdf_info, tmp_path, mock_writer)

            # Verify calls
            assert mock_writer.add_outline_item.call_count == 3  # noqa: PLR2004
            assert mock_writer.append.call_count == 2  # noqa: PLR2004
