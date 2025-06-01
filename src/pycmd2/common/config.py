import atexit
import logging

from pycmd2.common.cli import Client

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w


class TomlConfigMixin:
    """Toml配置管理器基类

    1. 通过继承该类，可以方便地管理配置文件
    2. 通过重写 _load 和 _save 方法，可以自定义配置文件的载入和保存方式
    3. 通过重写 _props 属性，可以自定义配置文件中保存的属性
    4. 通过重写 NAME 属性，可以自定义配置文件名

    Args:
        NAME: 配置文件名

    """

    NAME: str = ""

    def __init__(self) -> None:
        self._config_file = Client.SETTINGS_DIR / f"{self.NAME}.toml"
        self._config = {}

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
            for attr in self._props.keys():
                if attr in self._config and self._config[attr] != getattr(
                    self, attr
                ):
                    logging.info(f"设置属性: {attr} = {self._config[attr]}")
                    setattr(self, attr, self._config[attr])
                    self._props[attr] = self._config[attr]

        # 保存配置数据到文件
        atexit.register(self._save)

    def _load(self):
        if not self._config_file.exists():
            logging.error(f"未找到配置文件: {self._config_file}")
            self._config = {}
            return

        try:
            with open(self._config_file, "rb") as f:
                self._config = tomllib.load(f)
        except Exception as e:
            logging.error(f"载入配置错误: {e}")
            self._config = {}
        else:
            logging.info(f"载入配置: {self._config_file}")

    def _save(self):
        try:
            with open(self._config_file, "wb") as f:
                tomli_w.dump(self._props, f)
        except Exception as e:
            logging.error(f"保存配置错误: {e}")
        else:
            logging.info(f"保存配置: {self._config_file}")
