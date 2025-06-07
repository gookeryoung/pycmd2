import atexit
import logging
import re
import shutil
from dataclasses import dataclass

from pycmd2.common.cli import get_client

try:
    import tomllib  # type: ignore[import]
except ModuleNotFoundError:
    import tomli as tomllib

from typing import TYPE_CHECKING

import tomli_w

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "TomlConfigMixin",
    "clear_config",
    "to_snake_case",
]

cli = get_client()
logger = logging.getLogger(__name__)


def clear_config() -> None:
    """清除配置文件."""
    if cli.settings_dir.exists():
        shutil.rmtree(str(cli.settings_dir))


def to_snake_case(name: str) -> str:
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
    """Toml配置管理器基类.

    1. 通过继承该类, 可以方便地管理配置文件
    2. 通过重写 _load 和 _save 方法, 可以自定义配置文件的载入和保存方式
    3. 通过重写 _props 属性, 可以自定义配置文件中保存的属性
    4. 通过重写 NAME 属性, 可以自定义配置文件名
    """

    NAME: str = ""

    def __init__(self) -> None:
        cls_name = to_snake_case(type(self).__name__).replace("_config", "")
        self.config_file: Path = cli.settings_dir / f"{cls_name}.toml"
        self._config = {}

        # 创建父文件夹
        if not cli.settings_dir.exists():
            cli.settings_dir.mkdir(parents=True)

        # 载入配置
        self.load()

        # 获取属性
        self._props = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }

        # 写入配置数据到实例
        if self._config:
            for attr in self._props:
                if attr in self._config and self._config[attr] != getattr(
                    self,
                    attr,
                ):
                    logger.info(f"设置属性: {attr} = {self._config[attr]}")
                    setattr(self, attr, self._config[attr])
                    self._props[attr] = self._config[attr]

        # 保存配置数据到文件
        atexit.register(self.save)

    def load(self) -> None:
        """从文件载入配置."""
        if not self.config_file.exists():
            logger.error(f"未找到配置文件: {self.config_file}")
            return

        try:
            with self.config_file.open("rb") as f:
                self._config = tomllib.load(f)
        except Exception as e:
            msg = f"读取配置错误: {e.__class__.__name__}: {e}"
            logger.exception(msg)
            return
        else:
            logger.info(f"载入配置: [green]{self.config_file}")

    def save(self) -> None:
        """保存配置到文件."""
        try:
            with self.config_file.open("wb") as f:
                tomli_w.dump(self._props, f)
        except Exception as e:
            msg = f"保存配置错误: {e.__class__.__name__}: {e}"
            logger.exception(msg)
        else:
            logger.info(f"保存配置: [green]{self.config_file}")
