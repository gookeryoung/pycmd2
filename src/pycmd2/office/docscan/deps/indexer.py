import pathlib
import time
import typing

from jieba.analyse import ChineseAnalyzer
from whoosh.fields import ID
from whoosh.fields import Schema
from whoosh.fields import TEXT
from whoosh.index import create_in
from whoosh.index import FileIndex
from whoosh.query import Regex

from pycmd2.office.docscan.deps.readers.archive import ALL_READERS
from pycmd2.office.docscan.deps.readers.base import BaseReader

MatchContent = typing.NamedTuple(
    "MatchContent", (("filename", str), ("match_text", typing.List[bytes]))
)


class Indexer:
    def __init__(
        self,
        search_dir: pathlib.Path,
        index_dir: pathlib.Path,
    ) -> None:
        self.search_dir = search_dir
        self.index_dir = index_dir
        self.index: typing.Optional[FileIndex] = None
        self.schema = Schema(
            title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
            path=ID(stored=True),
            content=TEXT(stored=True),
        )

        self._create_index_dir()
        self._parse_search_dir()

    def _create_index_dir(self):
        if not self.index_dir.exists():
            self.index_dir.mkdir(exist_ok=True, parents=True)

    def _parse_search_dir(self):
        files = []
        for ext in ALL_READERS.keys():
            files.extend(self.search_dir.rglob(f"*.{ext.lower()}"))

        if len(files) != 0:
            print(f"[*] 找到匹配后缀文件{len(files)=}, {files=}")

            self.index = create_in(self.index_dir, schema=self.schema)
            writer = self.index.writer()

            for file in files:
                t0 = time.perf_counter()
                reader: BaseReader = ALL_READERS.get(
                    file.suffix[1:], "Reader not found"
                )
                writer.add_document(
                    title=file.name, path=file.name, content=reader.read(file)
                )
                print(f"[*] {file=}文件索引用时: {time.perf_counter() - t0}s")

            writer.commit()
        else:
            print("[*] 未找到匹配后缀文件")

    def query_reg(self, text: str) -> typing.List[MatchContent]:
        query = Regex("content", text)
        matches: typing.List[MatchContent] = []

        if self.index is not None:
            with self.index.searcher() as s:
                results = s.search(query, terms=True)
                for hit in results:
                    matches.append(
                        MatchContent(
                            filename=hit["path"],
                            match_text=[x[1] for x in hit.matched_terms()],
                        )
                    )
            return matches
