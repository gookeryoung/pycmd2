"""Configuration settings application."""

from __future__ import annotations

from nicegui import ui

from pycmd2.web.components.navigator import create_page_with_navigation
from pycmd2.web.components.navigator import Navigator
from pycmd2.web.config import conf


class ConfigApp:
    """Configuration settings application."""

    ROUTER = "/settings/config"

    def __init__(self) -> None:
        """Initialize the configuration app."""
        self.config = conf

    def setup(self) -> None:
        """Setup the configuration page."""

        def page_content() -> None:
            with ui.card().classes("w-full"), ui.column().classes("w-full gap-4 p-6"):
                ui.label("Navigation Settings").classes("text-h5 font-bold mb-4")

                # Navigation position setting
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("Navigation Position").classes("text-body1")
                    ui.radio(
                        ["left", "top"],
                        value=self.config.navigation_position,
                        on_change=lambda e: self._update_navigation_position(e.value),
                    ).props("inline")

                ui.separator()

                # Show search setting
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("Show Search in Navigation").classes("text-body1")
                    ui.switch(
                        value=self.config.show_navigation_search,
                        on_change=lambda e: self._update_show_search(bool(e.value)),
                    )

                ui.separator()

                # Navigation width setting (only for left navigation)
                if self.config.navigation_position == "left":
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("Navigation Width").classes("text-body1")
                        ui.select(
                            ["250px", "300px", "350px", "400px"],
                            value=self.config.navigation_width,
                            on_change=lambda e: self._update_navigation_width(e.value),
                        ).props("dense")

                ui.separator()

                # Save button
                with ui.row().classes("w-full justify-end"):
                    ui.button("Save Settings", on_click=self._save_settings).props("color=primary")
                    ui.button("Reset to Default", on_click=self._reset_settings).props("color=secondary flat")

        # Create page with navigation
        navigator = Navigator("Settings")
        create_page_with_navigation(
            navigator=navigator,
            page_title="Configuration Settings",
            content_callback=page_content,
        )

    def _update_navigation_position(self, value: str) -> None:
        """Update navigation position.

        Args:
            value: New navigation position value
        """
        self.config.navigation_position = value
        ui.notify(f"Navigation position set to: {value}. Please refresh the page to see changes.", type="positive")

    def _update_show_search(self, value: bool) -> None:
        """Update show search setting.

        Args:
            value: New show search value
        """
        self.config.show_navigation_search = value
        ui.notify(f"Show search set to: {value}", type="positive")

    def _update_navigation_width(self, value: str) -> None:
        """Update navigation width.

        Args:
            value: New navigation width value
        """
        self.config.navigation_width = value
        ui.notify(f"Navigation width set to: {value}", type="positive")

    def _save_settings(self) -> None:
        """Save all settings."""
        self.config.save()
        ui.notify("Settings saved successfully! Please refresh the page to see changes.", type="positive")

    def _reset_settings(self) -> None:
        """Reset settings to default."""
        self.config.navigation_position = "left"
        self.config.show_navigation_search = True
        self.config.navigation_width = "300px"
        self.config.navigation_collapsed = False
        self.config.save()
        ui.notify("Settings reset to default! Please refresh the page to see changes.", type="info")
