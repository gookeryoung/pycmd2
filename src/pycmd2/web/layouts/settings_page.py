from pycmd2.web.components.main_footer import MainFooter
from pycmd2.web.components.main_navigator import get_main_navigator
from pycmd2.web.components.settings_content import get_settings_content
from pycmd2.web.config import conf
from pycmd2.web.config import WebServerConfig
from pycmd2.web.layouts.main_page import MainPage


class SettingsPage(MainPage):
    """设置导航器."""

    ROUTER = "/system/settings"

    def __init__(self) -> None:
        super().__init__()

        self.config: WebServerConfig = conf

    def setup_ui(self) -> None:
        """设置导航器 UI."""
        get_main_navigator().setup_ui()
        get_settings_content().setup_ui()
        MainFooter().render()
