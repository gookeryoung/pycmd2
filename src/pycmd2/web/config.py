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

    # 主页样式
    MAIN_PAGE_STYLE = """
<style>
    .tool-card {
        transition: all 0.3s ease;
        border-radius: 12px;
    }
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .category-icon {
        font-size: 2rem !important;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
    }
    .app-title {
        font-weight: 600;
    }
    .app-description {
        color: #6b7280;
        font-size: 0.875rem;
    }
    .stat-card {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .hidden-card {
        display: none;
    }
</style>
"""

    # 导航样式
    NAVIGATOR_STYLE = """
<style>
.navigation-group .q-expansion-item__header {
    border-radius: 8px;
    margin-bottom: 4px;
    background-color: transparent;
}
.navigation-group .q-expansion-item__header:hover {
    background-color: rgba(156, 163, 175, 0.1);
}
.dark .navigation-group .q-expansion-item__header:hover {
    background-color: rgba(75, 85, 99, 0.3);
}
.navigation-item {
    border-radius: 6px;
    margin: 2px 0;
}
.navigation-item .q-btn {
    border-radius: 6px;
    transition: all 0.2s ease;
}
.navigation-item .q-btn:hover {
    transform: translateX(4px);
}
.q-drawer {
    border-right: 1px solid #e5e7eb;
}
.dark .q-drawer {
    border-right: 1px solid #374151;
}
.navigation-item .q-badge {
    font-size: 10px;
    padding: 2px 6px;
    min-height: 16px;
}
.top-navigation {
    border-bottom: 1px solid #e5e7eb;
    background-color: #f9fafb;
    position: sticky;
    top: 0;
    z-index: 1000;
}
.dark .top-navigation {
    border-bottom: 1px solid #374151;
    background-color: #1f2937;
}
.top-nav-item .q-btn:hover {
    transform: translateY(-2px);
}
.q-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 2000 !important;
}
.q-page {
    padding-top: 120px !important;
}
@media (max-width: 600px) {
    .navigation-item .q-btn {
        font-size: 14px;
    }
    .navigation-group .q-expansion-item__header {
        font-size: 15px;
    }
    .top-navigation {
        flex-direction: column;
    }
}
</style>
"""


conf = WebServerConfig.get_instance()
