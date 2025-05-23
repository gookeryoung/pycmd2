import os

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
