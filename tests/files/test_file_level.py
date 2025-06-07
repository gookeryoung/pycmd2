from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.pycmd2.files.file_level import add_level_mark
from src.pycmd2.files.file_level import FileLevelConfig
from src.pycmd2.files.file_level import main
from src.pycmd2.files.file_level import remove_level_and_digital_mark
from src.pycmd2.files.file_level import remove_marks
from src.pycmd2.files.file_level import rename

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_config() -> FileLevelConfig:
    return FileLevelConfig()


@pytest.fixture
def test_files(tmp_path: Path) -> list[Path]:
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


def test_remove_marks(mock_config: FileLevelConfig) -> None:  # noqa: ARG001
    # 测试移除标记
    assert remove_marks("file(PUB).txt", ["PUB"]) == "file.txt"
    assert remove_marks("file(NOR).txt", ["NOR"]) == "file.txt"
    assert remove_marks("file(INT)(1).txt", ["INT"]) == "file(1).txt"
    assert remove_marks("file(CON).txt", ["CON"]) == "file.txt"


def test_remove_level_and_digital_mark(mock_config: FileLevelConfig) -> None:  # noqa: ARG001
    # 测试移除级别和数字标记
    assert remove_level_and_digital_mark("file(PUB).txt") == "file.txt"
    assert remove_level_and_digital_mark("file(1).txt") == "file.txt"
    assert remove_level_and_digital_mark("file(INT)(2).txt") == "file.txt"
    assert remove_level_and_digital_mark("file.txt") == "file.txt"


def test_add_level_mark(test_files: list[Path], tmp_path: Path) -> None:
    # 测试添加级别标记
    file = test_files[0]
    # 级别1
    new_path = add_level_mark(file, 1, 0)
    assert new_path.name == "test1(PUB).txt"

    # 级别2
    new_path = add_level_mark(file, 2, 0)
    assert new_path.name == "test1(INT).txt"

    # 测试冲突处理
    conflict_file = tmp_path / "test1(PUB).txt"
    conflict_file.write_text("conflict")
    new_path = add_level_mark(file, 1, 0)
    assert new_path.name == "test1(PUB)(1).txt"


def test_rename(mocker: MockerFixture, test_files: list[Path]) -> None:
    mocker_rn = mocker.patch("pathlib.Path.rename")

    # 测试重命名函数
    rename(test_files[0], 1)

    # 验证Path.rename被调用
    mocker_rn.assert_called_once()
    # 检查参数是否正确
    args = mocker_rn.call_args[0]
    assert len(args) == 1
    assert str(args[0]).endswith("test1(PUB).txt")


def test_main(mocker: MockerFixture, test_files: list[Path]) -> None:
    mocker_func = mocker.patch("src.pycmd2.files.file_level.cli.run")

    # 测试主函数
    main(targets=test_files, level=1)
    mocker_func.assert_called_once()
