from __future__ import annotations

from nicegui import ui

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import register_component
from pycmd2.web.config import conf
from pycmd2.web.config import WebServerConfig


@register_component("settings-content")
class SettingsContent(BaseComponent):
    """主内容区域."""

    COMPONENT_ID = "settings-content"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config: WebServerConfig = conf

    def render(self) -> None:
        """页面内容."""
        with ui.card().classes("w-full"), ui.column().classes("w-full gap-4 p-6"):
            ui.label("导航设置").classes("text-h5 font-bold mb-4")

            # Navigation position setting
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("导航位置").classes("text-body1")
                ui.radio(
                    ["left", "top"],
                    value=self.config.navigation_position,
                    on_change=lambda e: self._update_navigation_position(e.value),
                ).props("inline")

            ui.separator()

            # Show search setting
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("导航中显示搜索").classes("text-body1")
                ui.switch(
                    value=self.config.show_navigation_search,
                    on_change=lambda e: self._update_show_search(bool(e.value)),
                )

            ui.separator()

            # Navigation width setting (only for left navigation)
            if self.config.navigation_position == "left":
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("导航宽度").classes("text-body1")
                    ui.select(
                        ["250px", "300px", "350px", "400px"],
                        value=self.config.navigation_width,
                        on_change=lambda e: self._update_navigation_width(e.value),
                    ).props("dense")

            ui.separator()

            # Save button
            with ui.row().classes("w-full justify-end"):
                ui.button("保存设置", on_click=self._save_settings).props("color=primary")
                ui.button("重置为默认", on_click=self._reset_settings).props("color=secondary flat")

    def _update_navigation_position(self, value: str) -> None:
        """更新导航位置.

        Args:
            value: 新的导航位置值
        """
        self.config.navigation_position = value
        ui.notify(f"导航位置设置为: {value}.请刷新页面查看更改.", type="positive")

    def _update_show_search(self, *, value: bool) -> None:
        """更新显示搜索设置.

        Args:
            value: 新的显示搜索值
        """
        self.config.show_navigation_search = value
        ui.notify(f"显示搜索设置为: {value}", type="positive")

    def _update_navigation_width(self, value: str) -> None:
        """更新导航宽度.

        Args:
            value: 新的导航宽度值
        """
        self.config.navigation_width = value
        ui.notify(f"导航宽度设置为: {value}", type="positive")

    def _save_settings(self) -> None:
        """保存所有设置."""
        self.config.save()
        ui.notify("设置保存成功! 请刷新页面查看更改.", type="positive")

    def _reset_settings(self) -> None:
        """重置设置为默认值."""
        self.config.navigation_position = "left"
        self.config.show_navigation_search = True
        self.config.navigation_width = "300px"
        self.config.navigation_collapsed = False
        self.config.save()
        ui.notify("设置已重置为默认值! 请刷新页面查看更改.", type="info")
