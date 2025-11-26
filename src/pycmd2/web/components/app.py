from __future__ import annotations


class BaseApp:
    """Web 应用程序的抽象基类."""

    ROUTER: str = ""

    def __init__(self) -> None:
        self._setup_navigator()

    def _setup_navigator(self) -> None:
        """获取主导航器实例."""
        from pycmd2.web.pages.main_page import get_main_navigator  # noqa: PLC0415

        main_nav = get_main_navigator()
        main_nav.setup_ui()
