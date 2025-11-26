from pycmd2.web.component import register_component
from pycmd2.web.components.main_footer import MainFooter
from pycmd2.web.components.main_navigator import get_main_navigator
from pycmd2.web.components.settings_content import get_settings_content
from pycmd2.web.pages.main_page import MainPage


@register_component("settings-page")
class SettingsPage(MainPage):
    """设置导航器."""

    ROUTER = "/system/settings"

    def render(self) -> None:
        """设置导航器 UI."""
        get_main_navigator().setup_ui()
        get_settings_content().setup_ui()
        MainFooter().render()
