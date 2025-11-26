from __future__ import annotations

from pycmd2.web.component import BaseComponent
from pycmd2.web.component import ComponentFactory


class BaseApp(BaseComponent):
    """Web 应用程序的抽象基类."""

    ROUTER: str = ""

    def build(self) -> None:
        """构建应用程序."""
        ComponentFactory.create("main-navigator", title="通用工作流工具包").build()
        super().build()
        ComponentFactory.create("main-footer", title="通用工作流工具包 © 2025").build()
