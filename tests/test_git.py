import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pycmd2.git.git_clean import cli as git_clean_cli
from pycmd2.git.git_init import cli as git_init_cli


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Fixture to create a temporary Git repository.

    Returns:
        Path: The path to the temporary Git repository.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir(parents=True)
    subprocess.run(["git", "init", repo_path], check=True)
    return repo_path


def test_git_clean(typer_runner: CliRunner, git_repo: Path) -> None:
    """Test the git_clean() method."""
    os.chdir(git_repo)
    test_file = git_repo / "test.txt"
    test_file.write_text("This is a test file.")

    result = typer_runner.invoke(git_clean_cli.app, [])
    assert result.exit_code == 0
    assert test_file.exists()

    result = typer_runner.invoke(git_clean_cli.app, ["-f"])
    assert result.exit_code == 0
    assert not test_file.exists()


def test_git_init(typer_runner: CliRunner, tmp_path: Path) -> None:
    """Test the git_init() method."""
    os.chdir(tmp_path)
    Path(tmp_path / "test.txt").touch()
    Path(tmp_path / "test02.txt").touch()

    result = typer_runner.invoke(git_init_cli.app, [])
    assert result.exit_code == 0

    # Check if the .git directory was created
    assert (tmp_path / ".git").exists()

    # Check if the initial commit was made
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "initial commit" in result.stdout
