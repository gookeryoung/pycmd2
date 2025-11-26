from pycmd2.web.component import ComponentFactory
from pycmd2.web.component import register_component
from pycmd2.web.pages.main_page import MainPage


@register_component("settings-page")
class SettingsPage(MainPage):
    """设置导航器."""

    COMPONENT_ID = "settings-page"
    ROUTER = "/system/settings"

    def render(self) -> None:
        """设置导航器 UI."""
        ComponentFactory.create("settings-content").build()
