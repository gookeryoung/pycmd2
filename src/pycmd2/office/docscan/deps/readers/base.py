import pathlib
import typing


class BaseReader:
    """Base class of readers.

    usage:
        reader = BaseReader()
        content = reader.read(file_path)
        ...
    """

    def __init__(self):
        pass

    def read(
        self, file_path: typing.Union[pathlib.Path, typing.IO[bytes]]
    ) -> str:
        pass
