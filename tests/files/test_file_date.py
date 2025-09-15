from pycmd2.files.file_date import remove_date_prefix


class TestFileDate:
    """测试 file_date 模块功能."""

    def test_remove_date_prefix(self) -> None:
        """测试移除日期前缀功能."""
        f1 = remove_date_prefix("20220101-hello.txt")
        assert f1 == "hello.txt"

        f2 = remove_date_prefix("20191112-my-hello.txt")
        assert f2 == "my-hello.txt"
