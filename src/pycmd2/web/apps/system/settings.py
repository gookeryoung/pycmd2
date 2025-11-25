"""配置设置应用程序."""

from __future__ import annotations

from pycmd2.web.layouts.settings_navigator import SettingsNavigator


class SettingsApp:
    """配置设置应用程序."""

    ROUTER = "/system/settings"

    def setup(self) -> None:
        """设置配置页面."""
        navigator = SettingsNavigator("配置设置")
        navigator.setup_page()
