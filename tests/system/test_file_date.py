from pathlib import Path

import pytest

from pycmd2.system.file_date import FileDateProc


class TestFileDate:
    """测试 file_date 模块功能."""

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("20220101-hello.txt", "hello"),
            ("20191112-my-hello.txt", "my-hello"),
        ],
    )
    def test_remove_date_prefix(
        self,
        filename: str,
        expected: str,
        tmp_path: Path,
    ) -> None:
        """测试移除日期前缀功能."""
        filepath = tmp_path / filename
        filepath.touch()

        t = FileDateProc(filepath)
        t.rename()

        assert t.filestem == expected

    @pytest.mark.parametrize(
        "filename",
        [
            ("20220101_hello.txt"),
            ("20220101_my-hello.txt"),
        ],
    )
    def test_remove_date_prefix_conflict(
        self,
        filename: str,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试移除日期前缀功能冲突."""
        monkeypatch.setattr(
            "pycmd2.system.file_date.FileDateProc._time_mark",
            "20220101",
        )

        filepath = tmp_path / filename
        filepath.touch()

        t = FileDateProc(filepath)
        t.rename()

        assert "is the same as" in caplog.text
