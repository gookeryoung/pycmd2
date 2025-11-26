from __future__ import annotations

from pycmd2.web.component import ComponentFactory


class BaseApp:
    """Web 应用程序的抽象基类."""

    ROUTER: str = ""

    def __init__(self) -> None:
        self._setup_navigator()

    def _setup_navigator(self) -> None:
        """获取主导航器实例."""
        ComponentFactory.create("main-navigator", title="通用工作流工具包").build()
