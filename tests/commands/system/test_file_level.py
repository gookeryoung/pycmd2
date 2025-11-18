from __future__ import annotations

from pathlib import Path

import pytest

from pycmd2.commands.system.file_level import conf
from pycmd2.commands.system.file_level import FileProcessor


class TestFileLevel:
    """测试 file_level 模块功能."""

    @pytest.fixture(autouse=True)
    def disable_rename(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Disable rename for all test cases."""
        monkeypatch.setattr("pathlib.Path.rename", lambda _, __: None)

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("file.txt", "file"),
            ("file(PUB).txt", "file"),
            ("file(NOR).txt", "file"),
            ("file(INT)[1].txt", "file[1]"),
            ("file(CON).txt", "file"),
        ],
    )
    def test_remove_marks(self, filename: str, expected: str) -> None:
        """测试移除标记功能."""
        t = FileProcessor(Path(filename), Path(filename).stem)
        t._remove_marks(["PUB", "NOR", "INT", "CON"])  # noqa: SLF001
        assert t.filestem == expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("file1[1][2][3].txt", "file1"),
            ("file2(PUB)(9).txt", "file2"),
            ("file3(NOR)(1】.txt", "file3"),
            ("file4(INT)(9).txt", "file4"),
            ("file(INT)(11).txt", "file(11)"),
        ],
    )
    def test_remove_level_and_digital_mark(
        self,
        filename: str,
        expected: str,
    ) -> None:
        """Test remove level and digital mark."""
        t = FileProcessor(Path(filename), Path(filename).stem)
        t.rename()

        assert t.filestem == expected

    @pytest.mark.parametrize(
        ("filepath", "filelevel", "expected"),
        [
            (Path("test1.txt"), 1, Path("test1(PUB).txt")),
            (Path("test2.txt"), 2, Path("test2(INT).txt")),
            (Path("test3.txt"), 3, Path("test3(CON).txt")),
            (Path("test4.txt"), 4, Path("test4(CLA).txt")),
        ],
    )
    def test_add_level_mark(
        self,
        filepath: Path,
        filelevel: int,
        expected: Path,
    ) -> None:
        """测试添加级别标记功能."""
        t = FileProcessor(filepath, filepath.stem)
        t._add_level_mark(filelevel)  # noqa: SLF001

        assert t.filestem == expected.stem

    def test_add_level_mark_conflict(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试添加级别标记冲突处理功能."""
        conflict_file = tmp_path / "test1(PUB).txt"
        conflict_file.write_text("conflict")

        t = FileProcessor(tmp_path / "test1.txt", "test1")
        t.rename(level=1)

        assert "already exists" in caplog.text

    def test_rename_equals_to_original(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test if rename equals to original."""
        t = FileProcessor(Path("test1(PUB).txt"), "test1")
        t.rename(1)

        assert "equals to original" in caplog.text


class TestFileLevelRenameReal:
    """Test file rename in real file system."""

    @pytest.mark.parametrize(
        ("filename", "level", "expected"),
        [
            ("test1[1](2](3】.txt", 1, "test1(普通).txt"),
            ("test2(8)(1).txt", 2, "test2(特别).txt"),
            ("test3(特别)(1】.txt", 3, "test3(CON).txt"),
            ("test4(普通).txt", 4, "test4(CLA).txt"),
        ],
    )
    def test_real_file_rename(
        self,
        monkeypatch: pytest.MonkeyPatch,
        filename: str,
        level: int,
        expected: str,
        tmp_path: Path,
    ) -> None:
        """Test real file rename."""
        # Setup mock levels
        monkeypatch.setattr(
            conf,
            "LEVELS",
            {
                "0": "",
                "1": "普通",
                "2": "特别,特殊",
                "3": "CON",
                "4": "CLA",
            },
        )

        # Create real test file
        filepath = tmp_path / filename
        filepath.touch()

        t = FileProcessor(filepath, filepath.stem)
        t.rename(level)

        assert t.filestem == expected.split(".", maxsplit=1)[0]
        assert (tmp_path / expected).exists()
