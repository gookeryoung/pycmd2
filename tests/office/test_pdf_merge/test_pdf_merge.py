import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest
from src.pycmd2.office.pdf_merge import PdfFileInfo, search_directory, main

@pytest.fixture
def test_dir():
    return Path(os.path.dirname(__file__)) / "test_dir1"

@pytest.fixture
def mock_cli():
    with patch("src.pycmd2.office.pdf_merge.cli") as mock:
        mock.cwd = Path("test_dir")
        mock.logger.error.return_value = None
        mock.logger.info.return_value = None
        yield mock

def test_pdf_file_info():
    # Test PdfFileInfo class
    pdf_info = PdfFileInfo(
        prefix="test",
        files=[Path("file1.pdf"), Path("file2.pdf")],
        children=[]
    )
    assert pdf_info.prefix == "test"
    assert len(pdf_info.files) == 2
    assert pdf_info.count() == 2
    assert "file1.pdf" in str(pdf_info)

def test_search_directory(test_dir):
    # Test search_directory function
    pdf_info = search_directory(test_dir, test_dir)
    assert pdf_info is not None
    assert len(pdf_info.files) == 2  # file1.pdf and file2.pdf
    assert len(pdf_info.children) == 1  # subdir

    # Check subdir content
    subdir_info = pdf_info.children[0]
    assert subdir_info.prefix == "subdir"
    assert len(subdir_info.files) == 1  # file3.pdf

@patch("src.pycmd2.office.pdf_merge.pypdf.PdfWriter")
def test_main(mock_writer, mock_cli, tmp_path):
    # Setup mock return values
    mock_pdf_info = MagicMock()
    mock_pdf_info.count.return_value = 2
    mock_pdf_info.prefix = "test"
    mock_pdf_info.files = [tmp_path / "file1.pdf", tmp_path / "file2.pdf"]
    mock_pdf_info.children = []

    # Create valid PDF files for testing
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 10 >>\nstream\nBT /F1 12 Tf 72 720 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000257 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n360\n%%EOF"
    for f in mock_pdf_info.files:
        f.write_bytes(pdf_content)

    with patch("src.pycmd2.office.pdf_merge.search_directory") as mock_search:
        mock_search.return_value = mock_pdf_info
        mock_cli.cwd = tmp_path

        # Run main function
        main()
        # Verify the main function's behavior with mocked data
        assert mock_pdf_info.merge_file_info.call_count == 1

        # Verify calls
        mock_search.assert_called_once_with(tmp_path, tmp_path)
        mock_pdf_info.merge_file_info.assert_called_with(
            mock_pdf_info, tmp_path, writer=mock_writer.return_value
        )
        mock_writer.return_value.write.assert_called_once()
        mock_writer.return_value.close.assert_called_once()

def test_main_with_no_files(mock_cli, caplog):
    with patch("src.pycmd2.office.pdf_merge.search_directory") as mock_search:
        mock_search.return_value = None

        # Run main function
        main()

        # Verify error logging was called with expected message
        assert "[*] 未发现待合并文件, 退出..." in caplog.text

def test_merge_file_info(mock_cli, tmp_path):
    # Test merge_file_info method
    pdf_info = PdfFileInfo(
        prefix="test",
        files=[tmp_path / "file1.pdf", tmp_path / "file2.pdf"],
        children=[]
    )

    # Create valid PDF files for testing
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 10 >>\nstream\nBT /F1 12 Tf 72 720 Td (Hello) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000018 00000 n \n0000000077 00000 n \n0000000178 00000 n \n0000000257 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n360\n%%EOF"
    for f in pdf_info.files:
        f.write_bytes(pdf_content)

    mock_writer = MagicMock()
    mock_writer.add_outline_item.return_value = "bookmark"

    # Mock the cli.run method
    def mock_run(func, files):
        for f in files:
            func(f)

    with patch("src.pycmd2.office.pdf_merge.cli.run", mock_run):
        mock_cli.cwd = tmp_path
        pdf_info.merge_file_info(pdf_info, tmp_path, mock_writer)

        # Verify calls
        assert mock_writer.add_outline_item.call_count == 3
        assert mock_writer.append.call_count == 2
