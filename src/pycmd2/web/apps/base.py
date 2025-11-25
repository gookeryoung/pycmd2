from abc import ABC
from abc import abstractmethod


class BaseApp(ABC):
    """Web 应用程序的抽象基类."""

    ROUTER: str = ""

    @abstractmethod
    def setup(self) -> None:
        """设置并初始化应用程序."""
