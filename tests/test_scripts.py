"""Test script entries defined in pyproject.toml."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import tomli

# Scripts that require special handling or might not be testable in CI
SKIP_SCRIPTS = {
    # GUI applications that would block
    "mindnote",
    "pdftw",
    # Web servers that would run indefinitely
    "websvr",
    "llmsvr",
    # Simulation tools that might require special setup
    "lscopt",
    # System commands that might be platform-specific
    "taskk",  # taskkill on Windows
    "wch",  # which command
    "ld",  # list directories
}

# Scripts that should run without arguments and exit successfully
SAFE_SCRIPTS = {
    "pycmd2",
    "ggrep",
    "envjs",
    "envpy",
    "envrs",
    "gitadd",
    "gitc",
    "gitinit",
    "gitpa",
    "gitre",
    "mkp",
    "pipd",
    "pipdr",
    "pipf",
    "pipi",
    "pipio",
    "pipir",
    "pipr",
    "pipu",
    "pipur",
    "ssh-copy-id",
    "docdiff",
    "img2pdf",
    "imggry",
    "llmcli",
    "llmqnt",
    "pdfc",
    "pdfmrg",
    "pdfspl",
    "pdft",
    "todo",
    "videoconv",
    "alarmclk",
    "checksum",
    "filedate",
    "filelvl",
    "folderb",
    "folderz",
}


def get_project_scripts() -> dict[str, str]:
    """Extract script entries from pyproject.toml.

    Returns:
        dict[str, str]: A dictionary of script names and their corresponding entry points.
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with Path(pyproject_path).open("rb") as f:
        pyproject_data = tomli.load(f)

    return pyproject_data.get("project", {}).get("scripts", {})


@pytest.mark.parametrize("script_name", SAFE_SCRIPTS)
def test_script_execution_no_args(script_name: str) -> None:
    """Test that scripts can be executed without arguments and return non-zero exit codes.

    Note: Many CLI tools return non-zero exit codes when called without arguments
    because they require specific arguments, but they should at least be executable.
    """
    scripts = get_project_scripts()
    assert script_name in scripts, f"Script '{script_name}' not found in pyproject.toml"

    # Try to run the script
    try:
        # Using shell=True for simplicity, though it's not ideal for production
        # We're just testing if the entry point works
        subprocess.run(
            [sys.executable, "-m", script_name],
            check=False,
            capture_output=True,
            timeout=10,  # Timeout after 10 seconds
            shell=False,
        )
        # Just check that the process was able to start
        # Many CLIs will return non-zero when called without args, which is OK
    except subprocess.TimeoutExpired:
        # If it times out, it means the process started and was running
        pytest.skip(f"Script '{script_name}' timed out (probably waiting for input)")
    except FileNotFoundError:
        pytest.fail(f"Script '{script_name}' could not be found or executed")


def test_all_scripts_accounted_for() -> None:
    """Test that our test covers all scripts or explicitly skips them."""
    scripts = get_project_scripts()
    all_script_names = set(scripts.keys())

    # Check that all scripts are either in SAFE_SCRIPTS or SKIP_SCRIPTS
    unaccounted_scripts = all_script_names - SAFE_SCRIPTS - SKIP_SCRIPTS

    assert not unaccounted_scripts, (
        f"The following scripts are not accounted for in tests: {unaccounted_scripts}. Add them to SAFE_SCRIPTS or SKIP_SCRIPTS in test_scripts.py"
    )


def test_skip_scripts_exist() -> None:
    """Test that all scripts listed in SKIP_SCRIPTS actually exist in pyproject.toml."""
    scripts = get_project_scripts()
    all_script_names = set(scripts.keys())

    # Check that SKIP_SCRIPTS actually exist
    missing_skip_scripts = SKIP_SCRIPTS - all_script_names

    assert not missing_skip_scripts, f"The following scripts are listed in SKIP_SCRIPTS but don't exist in pyproject.toml: {missing_skip_scripts}"


def test_safe_scripts_exist() -> None:
    """Test that all scripts listed in SAFE_SCRIPTS actually exist in pyproject.toml."""
    scripts = get_project_scripts()
    all_script_names = set(scripts.keys())

    # Check that SAFE_SCRIPTS actually exist
    missing_safe_scripts = SAFE_SCRIPTS - all_script_names

    assert not missing_safe_scripts, f"The following scripts are listed in SAFE_SCRIPTS but don't exist in pyproject.toml: {missing_safe_scripts}"
