import logging
import os
import shutil
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from pycmd2.common.settings import Settings


@pytest.fixture
def existing_config_dir(tmp_path):
    # Create a temporary directory that already exists
    existing_dir = tmp_path / "existing_config"
    existing_dir.mkdir()
    return existing_dir


@pytest.fixture
def non_existent_dir(tmp_path):
    # Create a temporary directory that doesn't exist
    non_existent = tmp_path / "nonexistent"
    # Ensure it doesn't exist before test
    if non_existent.exists():
        shutil.rmtree(non_existent)
    return non_existent


@pytest.fixture
def read_only_config_dir(tmp_path):
    """Create a read-only directory fixture"""
    dir_path = tmp_path / "readonly_config"
    dir_path.mkdir()
    # Make directory read-only
    os.chmod(dir_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    yield dir_path
    # Restore permissions to allow cleanup
    os.chmod(dir_path, stat.S_IRWXU)


def test_initialize_settings_with_existing_config_directory(
    existing_config_dir,
):
    """Test initialization when config directory already exists"""
    # Mock the logging.info method to verify it's not called
    with patch("logging.info") as mock_logging:
        # Initialize Settings with existing directory
        settings = Settings(
            config_dir=existing_config_dir,
            config_name="test",
            default_config=None,
        )

        # Verify the object was created with correct attributes
        assert settings.config_dir == existing_config_dir
        assert settings.config_file == existing_config_dir / "test.toml"
        assert settings.config == {}

        # Verify no directory was created (mkdir shouldn't be called)
        mock_logging.assert_not_called()


@patch.object(logging, "info")
def test_initialize_settings_with_non_existent_config_directory(mock_logging):
    """Test initialization when config directory doesn't exist"""
    # Setup
    non_existent_path = Path("/non/existent/path")
    config_name = "test"

    # Ensure the path doesn't exist before test
    if non_existent_path.exists():
        non_existent_path.rmdir()

    # Execute
    settings = Settings(
        config_dir=non_existent_path,
        config_name=config_name,
        default_config=None,
    )

    # Verify
    assert settings.config_dir == non_existent_path
    assert settings.config_file == non_existent_path / f"{config_name}.toml"
    assert non_existent_path.exists() is True
    mock_logging.assert_called_once_with(f"创建配置目录: {non_existent_path}")

    # Cleanup
    non_existent_path.rmdir()


def test_config_file_path_construction(existing_config_dir):
    """
    Verify correct config file path construction.
    Test that the config file path matches expected
    pattern (dir/config_name.toml)
    """
    # Create the directory to simulate existing config
    existing_config_dir.mkdir(parents=True, exist_ok=True)

    # Mock the logging.info method to verify it's not called
    with patch("logging.info") as mock_logging:
        # Initialize Settings with directory and config name
        settings = Settings(
            config_dir=existing_config_dir,
            config_name="test_config",
            default_config=None,
        )

        # Verify the config file path is constructed correctly
        expected_path = existing_config_dir / "test_config.toml"
        assert settings.config_file == expected_path
        assert str(settings.config_file).endswith("test_config.toml")

        # Verify no logging occurred (side check)
        mock_logging.assert_not_called()


def test_empty_default_config_handling(tmp_path):
    """
    Test initialization with None as default config.
    Verifies that an empty dictionary is stored in settings.config
    when default_config is None.
    """
    # Create a temporary config directory for testing
    existing_config_dir = tmp_path / "config"
    existing_config_dir.mkdir()

    # Mock the logging.info method
    with patch("logging.info") as mock_logging:
        # Initialize Settings with None as default_config
        settings = Settings(
            config_dir=existing_config_dir,
            config_name="test",
            default_config=None,
        )

        # Verify the object was created with correct attributes
        assert settings.config_dir == existing_config_dir
        assert settings.config_file == existing_config_dir / "test.toml"

        # Verify config is an empty dictionary
        assert settings.config == {}

        # Verify no logging occurred
        mock_logging.assert_not_called()


def test_no_logging_for_existing_directory(existing_config_dir):
    """
    Verify no logging occurs for existing directory when initializing settings.

    Args:
        existing_config_dir: Existing directory path fixture
    """
    # Mock the logging.info method to verify it's not called
    with patch("logging.info") as mock_logging:
        # Initialize Settings with existing directory
        Settings(
            config_dir=existing_config_dir,
            config_name="test",
            default_config=None,
        )

        # Verify no logging calls were made
        mock_logging.assert_not_called()


def test_initialize_settings_with_path_object(tmp_path):
    """
    Test initialization when config_dir is a Path object
    """
    # Create a Path object for testing
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()

    # Mock the logging.info method
    with patch("logging.info") as mock_logging:
        # Initialize Settings with Path object
        settings = Settings(
            config_dir=config_dir,
            config_name="test",
            default_config=None,
        )

        # Verify the object was created with correct attributes
        assert settings.config_dir == config_dir
        assert settings.config_file == config_dir / "test.toml"
        assert settings.config == {}

        # Verify no directory was created (mkdir shouldn't be called)
        mock_logging.assert_not_called()


def test_initialize_settings_with_string_path(tmp_path):
    """Test initialization when config_dir is provided as string path"""
    # Convert Path to string to test string path handling
    config_dir_str = str(tmp_path)

    # Initialize Settings with string path
    settings = Settings(
        config_dir=config_dir_str,
        config_name="test",
        default_config=None,
    )

    # Verify the object was created with correct attributes
    assert settings.config_dir == Path(config_dir_str)
    assert settings.config_file == Path(config_dir_str) / "test.toml"
    assert settings.config == {}


@pytest.mark.parametrize(
    "config_name,expected_file",
    [
        ("test", "test.toml"),
        ("config", "config.toml"),
        ("settings", "settings.toml"),
        ("my_config", "my_config.toml"),
        ("test.config", "test.config.toml"),
    ],
)
def test_config_name_handling(existing_config_dir, config_name, expected_file):
    """检验配置名称处理"""
    with patch("logging.info"):
        settings = Settings(
            config_dir=existing_config_dir,
            config_name=config_name,
            default_config=None,
        )

        assert settings.config_file == existing_config_dir / expected_file


def test_initialize_settings_with_read_only_config_directory(
    read_only_config_dir,
):
    """Test initialization when config directory exists and is read-only"""
    # Mock the logging.info method to verify it's not called
    with patch("logging.info") as mock_logging:
        # Initialize Settings with read-only directory
        settings = Settings(
            config_dir=read_only_config_dir,
            config_name="test",
            default_config=None,
        )

        # Verify the object was created with correct attributes
        assert settings.config_dir == read_only_config_dir
        assert settings.config_file == read_only_config_dir / "test.toml"
        assert settings.config == {}

        # Verify no directory modification was attempted
        # (mkdir shouldn't be called)
        mock_logging.assert_not_called()
