"""Web configuration settings."""

from __future__ import annotations

from pycmd2.config import TomlConfigMixin


class WebServerConfig(TomlConfigMixin):
    """Web application configuration."""

    # Navigation position: 'left' or 'top'
    navigation_position: str = "left"

    # Whether to show search in navigation
    show_navigation_search: bool = True

    # Navigation drawer width (only for left navigation)
    navigation_width: str = "300px"

    # Whether to collapse navigation by default (only for left navigation)
    navigation_collapsed: bool = False


conf = WebServerConfig()
