from __future__ import annotations

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
def test_dir() -> Path:
    return Path(__file__).parent / "test_pdf_merge" / "test_dir1"


@pytest.fixture
def mock_cli() -> Generator[MagicMock]:
    with patch("src.pycmd2.office.pdf_merge.cli") as mock:
        mock.cwd = Path("test_dir")
        mock.logger.error.return_value = None
        mock.logger.info.return_value = None
        yield mock


class TestPDFMerge:
    """PDF 合并测试."""

    @pytest.fixture(scope="class", autouse=True)
    def generate_pdf_files(self) -> None:
        """Generate test PDF files for merging."""

        def create_pdf(filename: str, text: str) -> None:
            pdf = FPDF()
            pdf.add_page()  # 添加一个页面
            pdf.set_font("Arial", size=12)  # 设置字体
            pdf.cell(
                0,
                10,
                txt=text,  # type: ignore  # noqa: PGH003
                ln=True,
            )  # 添加文本
            pdf.output(filename)  # 保存PDF

        def generate_test_files() -> None:
            # Create test directory structure
            Path("tests/office/test_pdf_merge/test_dir1").mkdir(
                parents=True,
                exist_ok=True,
            )
            Path("tests/office/test_pdf_merge/test_dir1/subdir").mkdir(
                parents=True,
                exist_ok=True,
            )

            # Create test PDF files
            create_pdf(
                "tests/office/test_pdf_merge/top_level.pdf",
                "Top level PDF",
            )
            create_pdf(
                "tests/office/test_pdf_merge/test_dir1/file1.pdf",
                "First level PDF 1",
            )
            create_pdf(
                "tests/office/test_pdf_merge/test_dir1/file2.pdf",
                "First level PDF 2",
            )
            create_pdf(
                "tests/office/test_pdf_merge/test_dir1/subdir/file3.pdf",
                "Second level PDF",
            )

        generate_test_files()

    def test_pdf_file_info(self) -> None:
        """测试 PdfFileInfo 类的基本功能."""
        pdf_info = PdfFileInfo(
            prefix="test",
            files=[Path("file1.pdf"), Path("file2.pdf")],
            children=[],
        )
        assert pdf_info.prefix == "test"
        assert len(pdf_info.files) == 2  # noqa: PLR2004
        assert pdf_info.count() == 2  # noqa: PLR2004
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

    @patch("src.pycmd2.office.pdf_merge.pypdf.PdfWriter")
    def test_main(
        self,
        mock_writer: MagicMock,
        mock_cli: MagicMock,
        tmp_path: Path,
    ) -> None:
        """测试 main 函数的行为."""
        mock_pdf_info = MagicMock()
        mock_pdf_info.count.return_value = 2
        mock_pdf_info.prefix = "test"
        mock_pdf_info.files = [tmp_path / "file1.pdf", tmp_path / "file2.pdf"]
        mock_pdf_info.children = []

        # Create valid PDF files for testing
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 10 >>\nstream\nBT /F1 12 Tf 72 720 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000257 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n360\n%%EOF"  # noqa: E501
        for f in mock_pdf_info.files:
            f.write_bytes(pdf_content)

        with patch(
            "src.pycmd2.office.pdf_merge.search_directory",
        ) as mock_search:
            mock_search.return_value = mock_pdf_info
            mock_cli.cwd = tmp_path

            # Run main function
            main()
            # Verify the main function's behavior with mocked data
            assert mock_pdf_info.merge_file_info.call_count == 1

            # Verify calls
            mock_search.assert_called_once_with(tmp_path, tmp_path)
            mock_pdf_info.merge_file_info.assert_called_with(
                mock_pdf_info,
                tmp_path,
                writer=mock_writer.return_value,
            )
            mock_writer.return_value.write.assert_called_once()
            mock_writer.return_value.close.assert_called_once()

    def test_main_with_no_files(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 main 函数在没有待合并文件时的行为."""
        with patch(
            "src.pycmd2.office.pdf_merge.search_directory",
        ) as mock_search:
            mock_search.return_value = None

            # Run main function
            main()

            # Verify error logging was called with expected message
            assert "[*] 未发现待合并文件, 退出..." in caplog.text

    def test_merge_file_info(self, mock_cli: MagicMock, tmp_path: Path) -> None:
        """测试 PdfFileInfo.merge_file_info 方法."""
        # Test merge_file_info method
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
