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
        self._config = {}

        # 创建父文件夹
        if not cli.settings_dir.exists():
            cli.settings_dir.mkdir(parents=True)

        # 载入配置
        self.load()

        # 获取属性
        self._attrs = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }

        logger.info(f"Getting attributes: {self._attrs}")

        # 写入配置数据到实例
        if self._config:
            for attr in self._attrs:
                if attr in self._config and self._config[attr] != getattr(
                    self,
                    attr,
                ):
                    logger.info(
                        f"Setting attributes: {attr} = {self._config[attr]}",
                    )
                    setattr(self, attr, self._config[attr])
                    self._attrs[attr] = self._config[attr]

        # 保存配置数据到文件
        atexit.register(self.save)

    def setattr(self, attr: str, value: object) -> None:
        """设置属性."""
        if attr in self._attrs:
            logger.info(f"Setting attributes: {attr} = {value}")
            self._attrs[attr] = value

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
                self._config = tomllib.load(f)
        except Exception as e:
            msg = f"Read config error: {e.__class__.__name__}: {e}"
            logger.exception(msg)
            return
        else:
            logger.info(f"Load config: [green]{self._config_file}")

    def save(self) -> None:
        """保存配置到文件."""
        console = Console()
        try:
            with self._config_file.open("wb") as f:
                console.print(f"Save configs: {self._config_file}")
                console.print(f"Configurations: {self._attrs}")
                tomli_w.dump(self._attrs, f)
        except PermissionError as e:
            msg = f"Save config error: {e.__class__.__name__!s}: {e!s}"
            console.print(msg)
