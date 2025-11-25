"""配置设置应用程序."""

from __future__ import annotations

from pycmd2.web.config import conf
from pycmd2.web.config import WebServerConfig
from pycmd2.web.layouts.settings_navigator import SettingsNavigator


class SettingsApp:
    """配置设置应用程序."""

    ROUTER = "/settings/config"

    def __init__(self) -> None:
        """初始化配置应用程序."""
        self.config: WebServerConfig = conf

    def setup(self) -> None:
        """设置配置页面."""
        navigator = SettingsNavigator("配置设置")
        navigator.setup_page()
