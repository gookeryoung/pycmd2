from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.pycmd2.files.file_level import FileRenameTarget


class TestFileLevel:
    """测试 file_level 模块功能."""

    @pytest.fixture(autouse=True)
    def disable_rename(self) -> None:
        """Disable rename for all test cases."""
        patch("pathlib.Path.rename", side_effect=lambda _: None).start()

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
        t = FileRenameTarget(Path(filename), Path(filename).stem)
        t._remove_marks(["PUB", "NOR", "INT", "CON"])  # noqa: SLF001
        assert t.filestem == expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("file[1].txt", "file"),
            ("file(PUB)(9).txt", "file"),
            ("file(NOR)(1】.txt", "file"),
            ("file(INT)(9).txt", "file"),
            ("file(INT)(11).txt", "file(11)"),
        ],
    )
    def test_remove_level_and_digital_mark(
        self,
        filename: str,
        expected: str,
    ) -> None:
        """Test remove level and digital mark."""
        t = FileRenameTarget(Path(filename), Path(filename).stem)
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
        t = FileRenameTarget(filepath, filepath.stem)
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

        t = FileRenameTarget(tmp_path / "test1.txt", "test1")
        t.rename(level=1)

        assert "already exists" in caplog.text

    def test_rename_equals_to_original(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test if rename equals to original."""
        t = FileRenameTarget(Path("test1(PUB).txt"), "test1")
        t.rename(1)

        assert "equals to original" in caplog.text
