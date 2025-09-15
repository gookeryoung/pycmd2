from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.pycmd2.files.file_level import add_level_mark
from src.pycmd2.files.file_level import main
from src.pycmd2.files.file_level import remove_level_and_digital_mark
from src.pycmd2.files.file_level import remove_marks
from src.pycmd2.files.file_level import rename


class TestFileLevel:
    """测试 file_level 模块功能."""

    @pytest.fixture
    def test_files(self, tmp_path: Path) -> list[Path]:
        """Create test files.

        Returns:
            List of test files.
        """
        # 创建测试文件
        files = [
            tmp_path / "test1.txt",
            tmp_path / "test2(PUB).txt",
            tmp_path / "test3(1).txt",
            tmp_path / "test4(INT)(1).txt",
        ]
        for f in files:
            f.write_text("test content")

        return files

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("file.txt", "file.txt"),
            ("file(PUB).txt", "file.txt"),
            ("file(NOR).txt", "file.txt"),
            ("file(INT)[1].txt", "file[1].txt"),
            ("file(CON).txt", "file.txt"),
        ],
    )
    def test_remove_marks(self, filename: str, expected: str) -> None:
        """测试移除标记功能."""
        assert remove_marks(filename, ["PUB", "NOR", "INT", "CON"]) == expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("file[1].txt", "file.txt"),
            ("file(PUB)(9).txt", "file.txt"),
            ("file(NOR)(1】.txt", "file.txt"),
            ("file(INT)(11).txt", "file(11).txt"),
        ],
    )
    def test_remove_level_and_digital_mark(
        self,
        filename: str,
        expected: str,
    ) -> None:
        """测试移除级别和数字标记功能."""
        assert remove_level_and_digital_mark(filename) == expected

    @pytest.mark.parametrize(
        ("filepath", "filelevel", "suffix", "expected"),
        [
            (Path("test0(PUB).txt"), 0, 0, Path("test0.txt")),
            (Path("test1.txt"), 1, 0, Path("test1(PUB).txt")),
            (Path("test2.txt"), 2, 0, Path("test2(INT).txt")),
            (Path("test3.txt"), 3, 0, Path("test3(CON).txt")),
            (Path("test4.txt"), 4, 0, Path("test4(CLA).txt")),
        ],
    )
    def test_add_level_mark(
        self,
        filepath: Path,
        filelevel: int,
        suffix: int,
        expected: Path,
    ) -> None:
        """测试添加级别标记功能."""
        assert add_level_mark(filepath, filelevel, suffix) == expected

    def test_add_level_mark_conflict(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试添加级别标记冲突处理功能."""
        conflict_file = tmp_path / "test1(PUB).txt"
        conflict_file.write_text("conflict")

        origin_file = tmp_path / "test1.txt"
        new_path = add_level_mark(origin_file, 1, 0)
        assert new_path.name == "test1(PUB)(1).txt"

        assert "already exists." in caplog.text

    @patch("pathlib.Path.rename")
    def test_rename(
        self,
        mock_rename: MagicMock,
        test_files: list[Path],
    ) -> None:
        """测试重命名功能."""
        # 测试重命名函数
        rename(test_files[0], 1)

        # 验证Path.rename被调用
        mock_rename.assert_called_once()

        # 检查参数是否正确
        args = mock_rename.call_args[0]
        assert len(args) == 1
        assert str(args[0]).endswith("test1(PUB).txt")

    @patch("src.pycmd2.files.file_level.cli.run")
    def test_main(
        self,
        mock_cli_run: MagicMock,
        test_files: list[Path],
    ) -> None:
        """测试主函数功能."""
        # 测试主函数
        main(targets=test_files, level=1)

        mock_cli_run.assert_called_once()
