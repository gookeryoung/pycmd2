import pathlib
import unittest

from pycmd2.office.docscan.deps.indexer import Indexer

SAMPLE_INDEXER = Indexer(
    search_dir=pathlib.Path("") / "data", index_dir=pathlib.Path("indexer")
)


class TestIndexer(unittest.TestCase):
    def test_query_reg_match_txt_en(self):
        match_contents = SAMPLE_INDEXER.query_reg("world")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_txt_cn(self):
        match_contents = SAMPLE_INDEXER.query_reg("蒜蓉")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 2)

    def test_query_reg_match_docx(self):
        match_contents = SAMPLE_INDEXER.query_reg("libraries")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_xlsx(self):
        match_contents = SAMPLE_INDEXER.query_reg("绿米")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_xls(self):
        match_contents = SAMPLE_INDEXER.query_reg("飞行器")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_zip(self):
        match_contents = SAMPLE_INDEXER.query_reg("压缩包")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_pdf(self):
        match_contents = SAMPLE_INDEXER.query_reg("知识产权")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)

    def test_query_reg_match_pdf_normal(self):
        match_contents = SAMPLE_INDEXER.query_reg("华为")
        for m in match_contents:
            print(
                f"文件名: [{m.filename}], 匹配内容: "
                f"[{[x.decode('utf8') for x in m.match_text]}]"
            )
        self.assertGreaterEqual(len(match_contents), 1)


if __name__ == "__main__":
    unittest.main()
