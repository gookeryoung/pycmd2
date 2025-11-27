from nicegui import ui

from pycmd2.web.component import register_component
from pycmd2.web.components.app import BaseApp
from pycmd2.web.components.dbtable import DBTable


@register_component("dbtable-demo")
class DbTableDemoApp(BaseApp):
    """数据库表格示例应用."""

    ROUTER = "/demos/dbtable"

    def render(self) -> ui.element:
        """渲染应用.

        Returns:
            ui.element: 渲染结果
        """
        return DBTable(
            api_url="/api/users/",
            columns=[
                {"name": "id", "label": "ID"},
                {"name": "name", "label": "名称"},
                {"name": "email", "label": "邮箱"},
            ],
        ).build()


@ui.page(DbTableDemoApp.ROUTER)
def dbtable_demo_page() -> None:
    """数据库表格示例页面."""
    DbTableDemoApp().build()
