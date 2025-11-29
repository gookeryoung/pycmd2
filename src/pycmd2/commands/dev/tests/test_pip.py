import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pycmd2.commands.dev.piptools.pip_download import cli as pip_download_cli
from pycmd2.commands.dev.piptools.pip_download import cli as pip_download_req_cli
from pycmd2.commands.dev.piptools.pip_freeze import cli as pip_freeze_cli
from pycmd2.commands.dev.piptools.pip_install import cli as pip_install_cli
from pycmd2.commands.dev.piptools.pip_install_offline import (
    cli as pip_install_offline_cli,
)
from pycmd2.commands.dev.piptools.pip_install_req import cli as pip_install_req_cli
from pycmd2.commands.dev.piptools.pip_uninstall_req import cli as pip_uninstall_req_cli


@pytest.fixture
def requirments_file(tmp_path: Path) -> None:
    os.chdir(tmp_path)

    with (tmp_path / "requirements.txt").open("w", encoding="utf-8") as f:
        f.write("lxml==4.9.1\n")
        f.write("numba==0.58.1\n")


@pytest.mark.slow
class TestPip:
    """测试 pip 命令."""

    def test_pip_download(
        self,
        dir_tests: Path,
    ) -> None:
        """测试 pip download 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(pip_download_cli.app, ["lxml"])
        assert result.exit_code == 0

        files = list(dir_tests.glob("packages/lxml-*.whl"))
        assert len(files) == 1

    def test_pip_download_req(
        self,
        typer_runner: CliRunner,
        dir_tests: Path,
        requirments_file: None,  # noqa: ARG002
    ) -> None:
        """测试 pip download -r 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(pip_download_req_cli.app, [])
        assert result.exit_code == 0

        files = list(dir_tests.glob("packages/lxml-*.whl"))
        assert len(files) == 1

        files = list(dir_tests.glob("packages/numba-*.whl"))
        assert len(files) == 1

        files = list(dir_tests.glob("packages/numpy-*.whl"))
        assert len(files) == 1

    def test_pip_freeze(self, typer_runner: CliRunner, dir_tests: Path) -> None:
        """测试 pip freeze 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(pip_freeze_cli.app, [])
        assert result.exit_code == 0

        with (dir_tests / "requirements.txt").open("r", encoding="utf-8") as f:
            libs = {_.split("==")[0] for _ in f}
            assert "hatch" in libs
            assert "pytest" in libs

    def test_pip_install(
        self,
        typer_runner: CliRunner,
        dir_tests: Path,
    ) -> None:
        """测试 pip install 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(
            pip_install_cli.app,
            ["lxml", "typing-extensions"],
        )
        assert result.exit_code == 0

    def test_pip_install_offline(
        self,
        typer_runner: CliRunner,
        dir_tests: Path,
    ) -> None:
        """测试 pip install --no-index 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(
            pip_install_offline_cli.app,
            ["lxml", "typing-extensions"],
        )
        assert result.exit_code == 0

    def test_pip_install_req(
        self,
        typer_runner: CliRunner,
        requirments_file: None,  # noqa: ARG002
        dir_tests: Path,
    ) -> None:
        """测试 pip install -r 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(pip_install_req_cli.app, [])
        assert result.exit_code == 0

    def test_pip_uninstall_req(
        self,
        typer_runner: CliRunner,
        requirments_file: None,  # noqa: ARG002
        dir_tests: Path,
    ) -> None:
        """测试 pip uninstall -r 命令."""
        os.chdir(dir_tests)

        result = typer_runner.invoke(pip_uninstall_req_cli.app, [])
        assert result.exit_code == 0
