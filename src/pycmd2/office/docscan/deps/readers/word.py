import pathlib
import typing

import docx

from pycmd2.office.docscan.deps.readers.base import BaseReader


class WordReader(BaseReader):
    def __init__(self):
        super().__init__()

    def read(
        self, file_path: typing.Union[pathlib.Path, typing.IO[bytes]]
    ) -> str:
        document = docx.Document(file_path)
        content = "\n".join([p.text for p in document.paragraphs])
        return content
