import atexit
from dataclasses import dataclass

from rich.console import Console

from pycmd2.common.cli import get_client
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
    """Toml配置管理器基类.

    1. 通过继承该类, 可以方便地管理配置文件
    2. 通过重写 _load 和 _save 方法, 可以自定义配置文件的载入和保存方式
    3. 通过重写 _props 属性, 可以自定义配置文件中保存的属性
    4. 通过重写 NAME 属性, 可以自定义配置文件名
    """

    NAME: str = ""

    def __init__(self) -> None:
        cls_name = str_to_snake_case(type(self).__name__).replace("_config", "")
        self.NAME = cls_name if not self.NAME else self.NAME

        self._config_file: Path = cli.settings_dir / f"{cls_name}.toml"
        self._file_attrs = {}

        # 创建父文件夹
        if not cli.settings_dir.exists():
            cli.settings_dir.mkdir(parents=True)

        # 载入配置
        self.load()

        # 获取属性
        self._cls_attrs = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }

        logger.info(f"Getting attributes from default: [u]{self._cls_attrs}")

        # 写入配置数据到实例
        if self._file_attrs:
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
            logger.info(f"Diff attributes: [u]{diff_attrs}")
            for diff in diff_attrs:
                logger.info(
                    f"Setting attributes: [u]{diff.attr} = "
                    f"{self._file_attrs[diff.attr]}",
                )
                setattr(self, diff.attr, diff.file_value)
                self._cls_attrs[diff.attr] = diff.file_value

        # 保存配置数据到文件
        atexit.register(self.save)

    def setattr(self, attr: str, value: object) -> None:
        """设置属性."""
        if attr in self._cls_attrs:
            logger.info(f"Setting attributes: {attr} = {value}")
            self._cls_attrs[attr] = value

    @staticmethod
    def clear() -> None:
        """Delete all config files."""
        config_files = cli.settings_dir.glob("*.toml")
        for config_file in config_files:
            config_file.unlink()

    def load(self) -> None:
        """从文件载入配置."""
        if not self._config_file.exists():
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
            logger.info(f"Load config: [u green]{self._config_file}")

    def save(self) -> None:
        """保存配置到文件."""
        console = Console()
        try:
            with self._config_file.open("wb") as f:
                console.print(f"Save config to: [u]{self._config_file}")
                console.print(f"Configurations: {self._cls_attrs}")
                tomli_w.dump(self._cls_attrs, f)
        except PermissionError as e:
            msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
            console.print(msg)
