from __future__ import annotations

import atexit
from dataclasses import dataclass

from rich.console import Console

from pycmd2.client import get_client
from pycmd2.logger import Logger
from pycmd2.utils import str_to_snake_case

try:
    import tomllib  # type: ignore[import]
except ModuleNotFoundError:
    import tomli as tomllib


from pathlib import Path

import tomli_w

__all__ = [
    "TomlConfigMixin",
]

cli = get_client()
logger = Logger.get_instance(__name__)


@dataclass
class AttributeDiff:
    """Attribute difference."""

    __slots__ = ("attr", "cls_value", "file_value")

    attr: str
    file_value: object
    cls_value: object

    def __hash__(self) -> int:
        return hash((self.attr, str(self.file_value), str(self.cls_value)))


@dataclass
class TomlConfigMixin:
    """Base class for toml config mixin."""

    NAME: str = ""

    SHOW_LOGGING: bool = True

    def __init__(self) -> None:
        cls_name = str_to_snake_case(type(self).__name__).replace("_config", "")
        self.NAME = cls_name if not self.NAME else self.NAME

        self._config_file: Path = cli.settings_dir / f"{cls_name}.toml"
        self._file_attrs = {}

        if not cli.settings_dir.exists():
            if self.SHOW_LOGGING:
                logger.info(
                    f"Creating settings directory: [u]{cli.settings_dir}",
                )

            cli.settings_dir.mkdir(parents=True)

        self.load()

        if self.SHOW_LOGGING:
            logger.info(
                f"Compare attributes from default: [u]{self._cls_attrs}",
            )

        diff_attrs: list[AttributeDiff] = [
            AttributeDiff(
                attr,
                file_value=self._file_attrs[attr],
                cls_value=getattr(self, attr),
            )
            for attr in self._cls_attrs
            if attr in self._file_attrs
            and self._file_attrs[attr] != getattr(self, attr)
        ]
        if diff_attrs:
            if self.SHOW_LOGGING:
                logger.info(f"Diff attributes: [u]{diff_attrs}")

            for diff in diff_attrs:
                if self.SHOW_LOGGING:
                    logger.info(
                        f"Setting attributes: [u green]{diff.attr} = "
                        f"{self._file_attrs[diff.attr]}",
                    )

                setattr(self, diff.attr, diff.file_value)
                self._cls_attrs[diff.attr] = diff.file_value
        elif self.SHOW_LOGGING:
            logger.info(
                "No difference between config file and class attributes.",
            )

        atexit.register(self.save)

    def setattr(self, attr: str, value: object) -> None:
        """Set an attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if attr in self._cls_attrs:
            if self.SHOW_LOGGING:
                logger.info(f"Setting attributes: {attr} = {value}")

            setattr(self, attr, value)
        else:
            msg = f"Attribute {attr} not found in {self.__class__.__name__}."
            raise AttributeError(msg)

    @property
    def _cls_attrs(self) -> dict[str, object]:
        """Get all attributes of the class."""
        return {
            attr: getattr(self, attr)
            for attr in dir(self.__class__)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }

    @staticmethod
    def clear() -> None:
        """Delete all config files."""
        config_files = cli.settings_dir.glob("*.toml")
        for config_file in config_files:
            config_file.unlink()

    def load(self) -> None:
        """Load config from file."""
        if not self._config_file.is_file() or not self._config_file.exists():
            if self.SHOW_LOGGING:
                logger.error(f"Config file not found: {self._config_file}")
            return

        try:
            with self._config_file.open("rb") as f:
                self._file_attrs = tomllib.load(f)
        except Exception as e:
            if self.SHOW_LOGGING:
                msg = f"Read config error: {e.__class__.__name__}: {e}"
                logger.exception(msg)
            return
        else:
            if self.SHOW_LOGGING:
                logger.info(f"Load config: [u green]{self._config_file}")

    def save(self) -> None:
        """Save config to file."""
        console = Console()

        try:
            with self._config_file.open("wb") as f:
                if self.SHOW_LOGGING:
                    console.print(f"Save config to: [u]{self._config_file}")
                    console.print(f"Configurations: {self._cls_attrs}")
                tomli_w.dump(self._cls_attrs, f)
        except PermissionError as e:
            if self.SHOW_LOGGING:
                msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
                console.print(msg)
