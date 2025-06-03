import atexit
import logging
import re
import shutil
from dataclasses import dataclass

from pycmd2.common.cli import Client

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w

__all__ = [
    "TomlConfigMixin",
    "clear_config",
    "to_snake_case",
]


def clear_config():
    """清除配置文件."""
    if Client.SETTINGS_DIR.exists():
        shutil.rmtree(Client.SETTINGS_DIR)


def to_snake_case(name):
    """将驼峰命名转换为下划线命名, 处理连续大写字母的情况.

    例如: "HTTPRequest" -> "http_request".
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
        self._config_file = Client.SETTINGS_DIR / f"{cls_name}.toml"
        self._config = {}

        # 创建父文件夹
        if not Client.SETTINGS_DIR.exists():
            Client.SETTINGS_DIR.mkdir(parents=True)

        # 载入配置
        self._load()

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
                    logging.info(f"设置属性: {attr} = {self._config[attr]}")
                    setattr(self, attr, self._config[attr])
                    self._props[attr] = self._config[attr]

        # 保存配置数据到文件
        atexit.register(self._save)

    def _load(self):
        if not self._config_file.exists():
            logging.error(f"未找到配置文件: {self._config_file}")
            return

        try:
            with open(self._config_file, "rb") as f:
                self._config = tomllib.load(f)
        except Exception as e:
            logging.exception(f"载入配置错误: {e}")
            return
        else:
            logging.info(f"载入配置: [green]{self._config_file}")

    def _save(self):
        try:
            with open(self._config_file, "wb") as f:
                tomli_w.dump(self._props, f)
        except Exception as e:
            logging.exception(f"保存配置错误: {e}")
        else:
            logging.info(f"保存配置: [green]{self._config_file}")
