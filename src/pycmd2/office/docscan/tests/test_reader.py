import pathlib
import time
import unittest

from pycmd2.office.docscan.deps.readers.pdf import PdfReaderPDF
from pycmd2.office.docscan.deps.readers.pdf import PdfReaderPlumber


class TestPdfReader(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_read_pdf(self):
        pdf_file = pathlib.Path("") / "data" / "sample_10_pdf.pdf"

        t0 = time.perf_counter()
        pdf2_reader = PdfReaderPDF()
        pdf2_reader.read(pdf_file)
        t1 = time.perf_counter() - t0
        print(f"time used: {t1=} --- PdfReaderPDF2")

        t0 = time.perf_counter()
        pp_reader = PdfReaderPlumber()
        pp_reader.read(pdf_file)
        t1 = time.perf_counter() - t0
        print(f"time used: {t1=} --- PdfReaderPlumber")

    def test_read_pdf_large(self):
        pdf_file = pathlib.Path("") / "data" / "sample_11_pdf_large.pdf"

        t0 = time.perf_counter()
        pdf2_reader = PdfReaderPDF()
        pdf2_reader.read(pdf_file)
        t1 = time.perf_counter() - t0
        print(f"time used: {t1=} --- PdfReaderPDF2")

        t0 = time.perf_counter()
        pp_reader = PdfReaderPlumber()
        pp_reader.read(pdf_file)
        t1 = time.perf_counter() - t0
        print(f"time used: {t1=} --- PdfReaderPlumber")
