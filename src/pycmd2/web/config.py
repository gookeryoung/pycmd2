"""Web 应用配置设置."""

from __future__ import annotations

from pycmd2.config import TomlConfigMixin


class WebServerConfig(TomlConfigMixin):
    """Web 应用程序配置类.

    继承自 TomlConfigMixin, 支持将配置保存到 TOML 文件中.
    """

    # 导航位置: 'left' 或 'top'
    navigation_position: str = "left"

    # 是否在导航中显示搜索功能
    show_navigation_search: bool = True

    # 导航抽屉宽度
    navigation_width: str = "300px"

    # 是否默认折叠导航
    navigation_collapsed: bool = False


conf = WebServerConfig()
