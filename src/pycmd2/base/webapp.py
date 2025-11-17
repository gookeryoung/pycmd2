from abc import ABC
from abc import abstractmethod


class WebApp(ABC):
    """Abstract base class for web applications."""

    ROUTER: str = ""

    @abstractmethod
    def setup(self) -> None:
        """Setup the web application."""
