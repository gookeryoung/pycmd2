import pathlib
import typing

import pdfplumber
from pypdf import PdfReader

from pycmd2.office.docscan.deps.readers.base import BaseReader


class PdfReaderPlumber(BaseReader):
    def __init__(self):
        super().__init__()

    def read(
        self, file_path: typing.Union[pathlib.Path, typing.IO[bytes]]
    ) -> str:
        with pdfplumber.open(file_path) as pdf:
            all_pages_text = []
            for page in pdf.pages:
                all_pages_text.append(page.extract_text())
        content = "\n".join(all_pages_text)
        print(f"{file_path.name=}{content=}")
        return content


class PdfReaderPDF(BaseReader):
    def __init__(self):
        super().__init__()

    def read(
        self, file_path: typing.Union[pathlib.Path, typing.IO[bytes]]
    ) -> str:
        reader = PdfReader(file_path)
        page_text = [page.extract_text() for page in reader.pages]
        content = "\n".join(page_text)
        print(f"{file_path.name=}{content=}")
        return content
