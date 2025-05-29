import atexit
import json
import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from .cli import Client

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w


class Settings:
    def __init__(
        self,
        config_dir: Union[str, Path],
        config_name: str,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        """初始化配置管理器

        Args:
            config_dir: 配置文件目录路径
            default_config: 默认配置字典，当配置文件不存在时使用
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / f"{config_name}.toml"

        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"创建配置目录: {self.config_dir}")

        if self.config_file.exists():
            self.load_config()
        else:
            self.config = default_config if default_config else {}

    def load_config(self):
        try:
            with open(self.config_file, "rb") as f:
                self.config = tomllib.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"载入配置错误: {e}")
            self.config = {}
        except FileNotFoundError:
            logging.error(f"未找到配置文件: {self.config_file}")
            self.config = {}
        except Exception as e:
            logging.error(f"载入配置错误: {e}")
            self.config = {}
        else:
            logging.info(f"载入配置: {self.config_file}")

    def save_config(self):
        try:
            with open(self.config_file, "wb") as f:
                tomli_w.dump(self.config, f)
        except Exception as e:
            logging.error(f"保存配置错误: {e}")
        else:
            logging.info(f"保存配置: {self.config_file}")

    def get(self, key: str, default: Any = None) -> Any:
        val = self.config.get(key, default)
        if val is None:
            logging.warning(f"未找到配置: {key} = {val}, 返回默认值: {default}")
            return default

        logging.info(f"获取配置: {key} = {val}")
        return val

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()

    def delete(self, key: str):
        del self.config[key]
        self.save_config()


def get_settings(
    config_name: str,
    config_dir: Optional[Path] = None,
    default_config: Optional[Dict[str, Any]] = None,
) -> Settings:
    """获取配置管理器实例

    Args:
        config_name: 配置文件名称，不需要扩展名
        config_dir: 配置文件目录路径，默认为用户主目录下的 .pycmd2
        default_config: 默认配置字典，当配置文件不存在时使用
    例如:
        {
            "key": "value",
            "key2": 123,
            "key3": True,
            "key4": ["a", "b", "c"],
            "key5": {"subkey": "subvalue"}
        }

    Returns:
        Settings 实例
    """
    if config_dir is None:
        config_dir = Client.SETTINGS_DIR
    settings = Settings(config_dir, config_name, default_config)
    atexit.register(settings.save_config)
    return settings
