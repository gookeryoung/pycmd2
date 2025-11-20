"""测试 grep 命令."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from pycmd2.commands.system.grep import cli


class TestGrepCommand:
    """测试 grep 命令功能."""

    @pytest.fixture
    def sample_files(self, tmp_path: Path) -> Path:
        """创建测试文件.

        Returns:
            创建的测试文件路径.
        """
        # 创建测试文件
        file1 = tmp_path / "file1.txt"
        file1.write_text("hello world\nthis is a test\nfoo bar baz")

        file2 = tmp_path / "file2.txt"
        file2.write_text("python is great\nrust is fast\nprogramming languages")

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.txt"
        file3.write_text("grep is useful\nunix tools\ncommand line")

        return tmp_path

    def test_grep_found_matches(self, sample_files: Path, caplog: pytest.LogCaptureFixture) -> None:
        """测试能够找到匹配项."""
        runner = CliRunner()
        result = runner.invoke(cli.app, ["world", str(sample_files)])

        assert result.exit_code == 0
        assert "file1.txt" in caplog.text
        assert "hello world" in caplog.text
        assert "@1:" in caplog.text  # 行号

    def test_grep_no_matches(self, sample_files: Path, caplog: pytest.LogCaptureFixture) -> None:
        """测试没有匹配项的情况."""
        runner = CliRunner()
        result = runner.invoke(cli.app, ["nonexistent", str(sample_files)])

        assert result.exit_code == 0
        assert "未找到匹配项" in caplog.text

    def test_grep_directory_not_exist(self, caplog: pytest.LogCaptureFixture) -> None:
        """测试目录不存在的情况."""
        runner = CliRunner()
        result = runner.invoke(cli.app, ["pattern", "/non/existent/path"])

        assert result.exit_code == 0
        assert "未找到文件" in caplog.text

    def test_grep_single_file(self, sample_files: Path, caplog: pytest.LogCaptureFixture) -> None:
        """测试在单个文件中搜索."""
        runner = CliRunner()
        test_file = sample_files / "file1.txt"
        result = runner.invoke(cli.app, ["test", str(test_file)])

        assert result.exit_code == 0
        assert "file1.txt" in caplog.text
        assert "this is a test" in caplog.text
        assert "@2:" in caplog.text  # 第2行

    def test_grep_multiple_matches(self, sample_files: Path, caplog: pytest.LogCaptureFixture) -> None:
        """测试多个匹配项."""
        runner = CliRunner()
        result = runner.invoke(cli.app, ["is", str(sample_files)])

        assert result.exit_code == 0
        # 应该在多个文件中找到"is"
        assert "file1.txt" in caplog.text or "file2.txt" in caplog.text or "file3.txt" in caplog.text
        assert "is" in caplog.text
        assert "@1:" in caplog.text or "@2:" in caplog.text or "@3:" in caplog.text
