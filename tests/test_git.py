import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path):
    """Fixture to create a temporary Git repository."""
    import os
    import subprocess

    repo_path = tmp_path / "repo"
    os.makedirs(repo_path)
    subprocess.run(["git", "init", repo_path], check=True)
    return repo_path


def test_git_clean(typer_runner, git_repo):
    """Test the git_clean() method."""
    os.chdir(git_repo)
    test_file = git_repo / "test.txt"
    test_file.write_text("This is a test file.")

    from pycmd2.git.git_clean import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0
    assert test_file.exists()

    result = typer_runner.invoke(cli.app, ["-f"])
    assert result.exit_code == 0
    assert not test_file.exists()


def test_git_init(typer_runner, tmp_path):
    """Test the git_init() method."""
    os.chdir(tmp_path)
    Path(tmp_path / "test.txt").touch()
    Path(tmp_path / "test02.txt").touch()

    from pycmd2.git.git_init import cli

    result = typer_runner.invoke(cli.app, [])
    assert result.exit_code == 0

    # Check if the .git directory was created
    assert (tmp_path / ".git").exists()

    # Check if the initial commit was made
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert "initial commit" in result.stdout
