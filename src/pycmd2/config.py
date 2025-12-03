from __future__ import annotations

import atexit
import logging
import re
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import ClassVar
from typing import Dict
from typing import Type
from typing import TypeVar

import tomli_w

from pycmd2.client import get_client
from pycmd2.compat import tomllib

__all__ = [
    "TomlConfigMixin",
]

cli = get_client()
logger = logging.getLogger(__name__)

T = TypeVar("T", bound="TomlConfigMixin")


@dataclass(frozen=True)
class AttributeDiff:
    """属性差异."""

    attr: str
    file_value: object
    cls_value: object

    def __hash__(self) -> int:
        return hash((self.attr, str(self.file_value), str(self.cls_value)))


@lru_cache(maxsize=128)
def _to_snake_case(name: str) -> str:
    """优化的驼峰命名转下划线命名（使用缓存）.

    Returns:
        str: 下划线命名
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return name.lower()


class TomlConfigMixin:
    """TOML 配置混入基类."""

    name: str = ""

    # 为每个类单独维护实例字典
    _instances: ClassVar[Dict[Type, TomlConfigMixin]] = {}
    _exit_handler_registered: ClassVar[Dict[Type, bool]] = {}
    _instance_lock: threading.Lock = threading.Lock()

    def __init__(self, *, show_logging: bool = False) -> None:
        """初始化配置混入类.

        Args:
            show_logging (bool): 是否显示日志
        """
        if show_logging:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        cls_name = _to_snake_case(type(self).__name__).replace("_config", "")
        self.name = cls_name if not self.name else self.name

        self._config_file: Path = cli.settings_dir / f"{cls_name}.toml"
        self._file_attrs: dict[str, object] = {}

        if not cli.settings_dir.exists():
            logger.debug(
                f"创建设置目录: [u]{cli.settings_dir}",
            )

            cli.settings_dir.mkdir(parents=True)

        self.load()

        logger.debug(
            f"比较默认属性: [u]{self._cls_attrs}",
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
            logger.debug(f"差异属性: [u]{diff_attrs}")

            for diff in diff_attrs:
                logger.debug(
                    f"设置属性: [u green]{diff.attr} = {self._file_attrs[diff.attr]}",
                )

                setattr(self, diff.attr, diff.file_value)
                self._cls_attrs[diff.attr] = diff.file_value
        else:
            logger.debug(
                "配置文件与类属性之间无差异.",
            )

        # 只有在实例是首次创建时才注册atexit处理器
        if not self.__class__._exit_handler_registered.get(self.__class__, False):  # noqa: SLF001
            atexit.register(self.save)
            self.__class__._exit_handler_registered[self.__class__] = True  # noqa: SLF001

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        """获取单例对象.

        Returns:
            TomlConfigMixin: 单例对象
        """
        logger.debug(f"获取配置单例对象: [purple b]{cls.__name__}")

        # 使用类实例字典确保每个类有独立实例
        if cls not in cls._instances or cls._instances[cls] is None:
            with cls._instance_lock:
                # 双重检查锁定模式
                if cls not in cls._instances or cls._instances[cls] is None:
                    cls._instances[cls] = cls()
        return cls._instances[cls]  # type: ignore

    def get_fileattrs(self) -> dict[str, object]:
        """获取配置文件的所有属性.

        Returns:
            dict[str, object]: 配置文件的所有属性.
        """
        return self._file_attrs

    def setattr(self, attr: str, value: object) -> None:
        """设置属性.

        Args:
            attr (str): 属性名
            value (object): 属性值

        Raises:
            AttributeError: 如果属性不存在.
        """
        if attr in self._cls_attrs:
            logger.debug(f"设置属性: {attr} = {value}")

            setattr(self, attr, value)
        else:
            msg = f"属性 {attr} 在 {self.__class__.__name__} 中不存在."
            raise AttributeError(msg)

    @property
    def _cls_attrs(self) -> dict[str, object]:
        """获取类的所有属性.

        Returns:
            dict[str, object]: 类的所有属性
        """
        # 使用缓存避免重复计算
        if not hasattr(self, "_cached_cls_attrs"):
            self._cached_cls_attrs = {
                attr: getattr(self, attr)
                for attr in dir(self.__class__)
                if not attr.startswith("_") and not callable(getattr(self, attr))
            }
        return self._cached_cls_attrs

    @classmethod
    def clear(cls) -> None:
        """删除所有配置文件."""
        if not cli.settings_dir.exists():
            return

        config_files = cli.settings_dir.glob("*.toml")
        try:
            for config_file in config_files:
                config_file.unlink(missing_ok=True)
            # 清理实例缓存
            cls._instances.clear()
            cls._exit_handler_registered.clear()
        except PermissionError as e:
            msg = f"清除配置错误: {e.__class__.__name__}: {e}"
            logger.exception(msg)

    def load(self) -> None:
        """从文件加载配置."""
        if not self._config_file.is_file() or not self._config_file.exists():
            logger.error(f"配置文件未找到: {self._config_file}")
            return

        try:
            with self._config_file.open("rb") as f:
                self._file_attrs = tomllib.load(f)
        except Exception as e:
            logger.exception(f"读取配置失败: {e.__class__.__name__}")
            return
        else:
            logger.debug(f"加载配置: [u green]{self._config_file}")

    def save(self) -> None:
        """保存配置到文件."""
        # 确保目录存在
        if not cli.settings_dir.exists():
            cli.settings_dir.mkdir(parents=True)

        try:
            with self._config_file.open("wb") as f:
                tomli_w.dump(self._cls_attrs, f)

            logger.debug(f"保存配置到: [u]{self._config_file}")
            logger.debug(f"配置项: {self._cls_attrs}")
        except PermissionError as e:
            msg = f"保存配置错误: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
        except TypeError as e:
            logger.exception(f"self._cls_attrs: {self._cls_attrs}")
            msg = f"保存配置错误: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
        except Exception as e:
            msg = f"保存配置错误: {e.__class__.__name__!s}: {e!s}"
            logger.exception(msg)
