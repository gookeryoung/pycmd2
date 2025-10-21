from __future__ import annotations

import atexit
import logging
import re
from dataclasses import dataclass

from pycmd2.client import get_client

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
logger = logging.getLogger(__name__)


@dataclass
class AttributeDiff:
    """Attribute difference."""

    __slots__ = ("attr", "cls_value", "file_value")

    attr: str
    file_value: object
    cls_value: object

    def __hash__(self) -> int:
        return hash((self.attr, str(self.file_value), str(self.cls_value)))


def _to_snake_case(name: str) -> str:
    """将驼峰命名转换为下划线命名, 处理连续大写字母的情况.

    Args:
        name (str): 驼峰命名

    Returns:
        str: 下划线命名

    E.g.: "HTTPRequest" -> "http_request"
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # 处理连续大写字母的情况
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return name.lower()


@dataclass
class TomlConfigMixin:
    """Base class for toml config mixin."""

    NAME: str = ""

    def __init__(self, *, show_logging: bool = True) -> None:
        if show_logging:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        cls_name = _to_snake_case(type(self).__name__).replace("_config", "")
        self.NAME = cls_name if not self.NAME else self.NAME

        self._config_file: Path = cli.settings_dir / f"{cls_name}.toml"
        self._file_attrs = {}

        if not cli.settings_dir.exists():
            logger.debug(
                f"Creating settings directory: [u]{cli.settings_dir}",
            )

            cli.settings_dir.mkdir(parents=True)

        self.load()

        logger.debug(
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
            logger.debug(f"Diff attributes: [u]{diff_attrs}")

            for diff in diff_attrs:
                logger.debug(
                    f"Setting attributes: [u green]{diff.attr} = "
                    f"{self._file_attrs[diff.attr]}",
                )

                setattr(self, diff.attr, diff.file_value)
                self._cls_attrs[diff.attr] = diff.file_value
        else:
            logger.debug(
                "No difference between config file and class attributes.",
            )

        atexit.register(self.save)

    def get_fileattrs(self) -> dict[str, object]:
        """Get all attributes of the config file.

        Returns:
            dict[str, object]: All attributes of the config file.
        """
        return self._file_attrs

    def setattr(self, attr: str, value: object) -> None:
        """Set an attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if attr in self._cls_attrs:
            logger.debug(f"Setting attributes: {attr} = {value}")

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
        try:
            for config_file in config_files:
                config_file.unlink(missing_ok=True)
        except PermissionError as e:
            msg = f"Clear config error: {e.__class__.__name__}: {e}"
            logger.exception(msg)

    def load(self) -> None:
        """Load config from file."""
        if not self._config_file.is_file() or not self._config_file.exists():
            logger.error(f"Config file not found: {self._config_file}")
            return

        try:
            with self._config_file.open("rb") as f:
                self._file_attrs = tomllib.load(f)
        except Exception as e:
            msg = f"Read config error: {e.__class__.__name__}: {e}"
            logger.exception(msg)
            return
        else:
            logger.debug(f"Load config: [u green]{self._config_file}")

    def save(self) -> None:
        """Save config to file."""
        try:
            with self._config_file.open("wb") as f:
                tomli_w.dump(self._cls_attrs, f)

            logger.debug(f"Save config to: [u]{self._config_file}")
            logger.debug(f"Configurations: {self._cls_attrs}")
        except PermissionError as e:
            msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
        except TypeError as e:
            logger.exception(f"self._cls_attrs: {self._cls_attrs}")
            msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
        except Exception as e:
            msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
