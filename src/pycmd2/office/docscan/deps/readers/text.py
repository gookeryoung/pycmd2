import pathlib
import typing

import chardet

from pycmd2.office.docscan.deps.readers.base import BaseReader


class TextReader(BaseReader):
    def __init__(self):
        super().__init__()

    @staticmethod
    def detect_encoding(file_path):
        with open(file_path, "rb") as f:
            raw_data = f.read()
        return chardet.detect(raw_data)["encoding"]

    def read(
        self, file_path: typing.Union[pathlib.Path, typing.IO[bytes]]
    ) -> str:
        with open(file_path, encoding=self.detect_encoding(file_path)) as f:
            return "\n".join(f.readlines())
