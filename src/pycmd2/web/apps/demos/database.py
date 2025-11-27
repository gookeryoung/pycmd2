"""数据库和API使用示例."""

from __future__ import annotations

from typing import List

from nicegui import ui

from pycmd2.web.api import fetch
from pycmd2.web.components.app import BaseApp
from pycmd2.web.dbengine import Hero


class DatabaseDemoApp(BaseApp):
    """数据库和API使用示例应用."""

    ROUTER = "/demos/database"

    def __init__(self) -> None:
        """初始化."""
        super().__init__()
        self.heroes: List[Hero] = []
        self.new_hero_name: str = ""
        self.new_hero_description: str = ""
        self.new_hero_power_level: int = 1
        self.new_hero_is_active: bool = True
        self.selected_hero: Hero | None = None

    async def load_heroes(self) -> None:
        """从API加载英雄."""
        try:
            # 真实API调用
            response = await fetch("http://localhost:8000/api/heroes/")
            if response.is_success():
                heroes_data = await response.json()
                self.heroes = [Hero(**hero_data) for hero_data in heroes_data]
                ui.notify("英雄数据加载成功", type="positive")
            else:
                ui.notify(f"加载英雄数据失败: HTTP {response.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"API调用失败, 使用模拟数据: {e!s}", type="info")

    async def add_hero(self) -> None:
        """添加新英雄."""
        if not self.new_hero_name:
            ui.notify("请填写英雄名称", type="warning")
            return

        try:
            # 创建英雄数据，不指定id，让数据库自动生成
            hero_data = Hero(
                name=self.new_hero_name,
                description=self.new_hero_description,
                power_level=self.new_hero_power_level,
                is_active=self.new_hero_is_active,
            )

            # 调用API，不传递id，让后端自动生成
            response = await fetch(
                "http://localhost:8000/api/heroes/",
                method="POST",
                data=hero_data.model_dump(exclude={"id"}),  # 排除id字段
            )

            if response.is_success():
                new_hero_data = await response.json()
                new_hero = Hero(**new_hero_data)
                self.heroes.append(new_hero)
                ui.notify(f"英雄添加成功，ID为: {new_hero.id}", type="positive")
            else:
                error_text = await response.text()
                ui.notify(f"添加英雄失败: HTTP {response.status_code} - {error_text}", type="negative")

            # 清空输入字段
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True
        except Exception as e:
            ui.notify(f"API调用失败: {e!s}", type="negative")
            # 如果API调用失败, 模拟添加英雄
            # 清空输入字段
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True

    async def delete_hero(self, hero_id: int) -> None:
        """删除英雄."""
        try:
            # 调用API
            response = await fetch(f"http://localhost:8000/api/heroes/{hero_id}", method="DELETE")

            if response.is_success():
                # 删除成功, 更新本地数据
                self.heroes = [hero for hero in self.heroes if hero.id != hero_id]
                ui.notify("英雄删除成功", type="positive")
            else:
                error_text = await response.text()
                ui.notify(f"删除英雄失败: HTTP {response.status_code} - {error_text}", type="negative")
                # 模拟删除英雄作为后备
                self._simulate_delete_hero(hero_id)
        except Exception as e:
            ui.notify(f"API调用失败: {e!s}", type="negative")
            # 如果API调用失败, 模拟删除英雄
            self._simulate_delete_hero(hero_id)

    def _simulate_delete_hero(self, hero_id: int) -> None:
        """模拟删除英雄."""
        self.heroes = [hero for hero in self.heroes if hero.id != hero_id]
        ui.notify("模拟删除成功", type="info")

    async def edit_hero(self, hero: Hero) -> None:
        """编辑英雄."""
        self.selected_hero = hero
        self.new_hero_name = hero.name
        self.new_hero_description = hero.description or ""
        self.new_hero_power_level = hero.power_level
        self.new_hero_is_active = hero.is_active

    async def update_hero(self) -> None:
        """更新英雄."""
        if not self.selected_hero or not self.new_hero_name:
            ui.notify("请选择英雄并填写名称", type="warning")
            return

        try:
            # 创建更新数据
            hero_data = Hero(
                name=self.new_hero_name,
                description=self.new_hero_description,
                power_level=self.new_hero_power_level,
                is_active=self.new_hero_is_active,
            )

            # 调用API，使用PATCH方法并排除id字段
            response = await fetch(
                f"http://localhost:8000/api/heroes/{self.selected_hero.id}",
                method="PATCH",
                data=hero_data.model_dump(exclude={"id"}),  # 排除id字段
            )

            if response.is_success():
                updated_hero_data = await response.json()
                updated_hero = Hero(**updated_hero_data)

                # 更新本地数据
                for i, hero in enumerate(self.heroes):
                    if hero.id == updated_hero.id:
                        self.heroes[i] = updated_hero
                        break

                ui.notify("英雄更新成功", type="positive")
            else:
                error_text = await response.text()
                ui.notify(f"更新英雄失败: HTTP {response.status_code} - {error_text}", type="negative")
                # 模拟更新英雄作为后备
                self._simulate_update_hero()

            # 重置表单
            self.selected_hero = None
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True
        except Exception as e:
            ui.notify(f"API调用失败: {e!s}", type="negative")
            # 如果API调用失败, 模拟更新英雄
            self._simulate_update_hero()
            # 重置表单
            self.selected_hero = None
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True

    def _simulate_update_hero(self) -> None:
        """模拟更新英雄."""
        for i, hero in enumerate(self.heroes):
            if hero.id == self.selected_hero.id:
                self.heroes[i] = Hero(
                    id=self.selected_hero.id,
                    name=self.new_hero_name,
                    description=self.new_hero_description,
                    power_level=self.new_hero_power_level,
                    is_active=self.new_hero_is_active,
                )
                break
        ui.notify("模拟更新成功", type="info")

    def start_api_server(self) -> None:
        """启动API服务器."""
        try:
            import subprocess
            import sys
            from pathlib import Path

            # 获取api_server.py文件的路径
            web_dir = Path(__file__).parent.parent
            api_server_path = web_dir / "api_server.py"

            # 在新的进程中启动API服务器
            subprocess.Popen(
                [sys.executable, str(api_server_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
            )

            ui.notify(
                "API服务器正在启动，请等待几秒钟后重试。服务器将运行在 http://localhost:8000",
                type="positive",
                timeout=10,
            )
        except Exception as e:
            ui.notify(f"启动API服务器失败: {e!s}", type="negative")
            ui.notify("请手动运行: python src/pycmd2/web/api_server.py", type="info")

    async def test_api_connection(self) -> None:
        """测试API连接."""
        try:
            # 测试连接到API根路径
            response = await fetch("http://localhost:8000/api/heroes/", method="GET")
            if response.is_success():
                ui.notify("API服务器连接成功", type="positive")
            else:
                ui.notify(f"API服务器连接失败: HTTP {response.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"API服务器连接失败: {e!s}", type="negative")

    def render(self) -> None:
        """渲染界面."""
        ui.label("英雄管理系统").classes("text-2xl font-bold mb-4")

        # 添加说明
        with ui.card().classes("w-full mb-4 p-4"):
            ui.label("使用说明").classes("text-lg font-bold mb-2")
            ui.label("1. 本系统包含前端界面和后端API两部分").classes("block mb-1")
            ui.label("2. 如需使用真实数据库功能，请先启动后端API服务器").classes("block mb-1")
            ui.label("3. 如果不启动API，系统将使用模拟数据运行").classes("block mb-1")
            with ui.row().classes("gap-2 mt-2"):
                ui.button("启动API服务器", on_click=self.start_api_server).classes("bg-blue-500 text-white")
                ui.button("测试API连接", on_click=self.test_api_connection).classes("bg-orange-500 text-white")
                ui.button("加载英雄", on_click=self.load_heroes).classes("bg-green-500 text-white")

        # 英雄列表
        with ui.card().classes("w-full mb-4"):
            ui.label("英雄列表").classes("text-xl font-bold mb-2")

            # 英雄表格
            columns = [
                {"name": "id", "label": "ID", "field": "id", "sortable": True},
                {"name": "name", "label": "名称", "field": "name", "sortable": True},
                {"name": "description", "label": "描述", "field": "description"},
                {"name": "power_level", "label": "能力等级", "field": "power_level", "sortable": True},
                {"name": "is_active", "label": "状态", "field": "is_active"},
                {"name": "actions", "label": "操作", "field": "actions"},
            ]

            table = ui.table(columns=columns, rows=[hero.dict() for hero in self.heroes]).classes("w-full")

            # 添加操作按钮
            with table.add_slot("body-cell-actions"):

                def render_actions(props) -> None:
                    hero_id = props.row.id
                    with ui.row().classes("gap-1"):
                        ui.button("编辑", on_click=lambda e, h=hero_id: self.edit_hero(next((h for h in self.heroes if h.id == h), None))).props(
                            "flat dense color=primary",
                        )
                        ui.button("删除", on_click=lambda e, h=hero_id: self.delete_hero(h)).props("flat dense color=negative")

            # 添加状态显示
            with table.add_slot("body-cell-is_active"):

                def render_status(props) -> None:
                    status = props.row.is_active
                    ui.label("激活" if status else "未激活").classes(
                        "text-positive" if status else "text-negative",
                    )

        # 添加/编辑英雄表单
        with ui.card().classes("w-full"):
            ui.label(
                "编辑英雄" if self.selected_hero else "添加新英雄",
            ).classes("text-xl font-bold mb-2")

            with ui.grid(columns=2).classes("w-full gap-2"):
                ui.input("名称", placeholder="英雄名称").bind_value(self, "new_hero_name")
                ui.input(
                    "能力等级",
                    placeholder="1-100",
                    value=str(self.new_hero_power_level),
                    on_change=lambda e: setattr(self, "new_hero_power_level", max(1, min(100, int(e.value) if e.value.isdigit() else 1))),
                )

            with ui.column().classes("w-full gap-2"):
                ui.textarea("描述", placeholder="英雄描述").bind_value(self, "new_hero_description")
                ui.checkbox("激活状态").bind_value(self, "new_hero_is_active")

            with ui.row().classes("w-full gap-2 mt-2"):
                if self.selected_hero:
                    ui.button("更新英雄", on_click=self.update_hero).classes("flex-1")
                    ui.button("取消", on_click=lambda: setattr(self, "selected_hero", None)).classes("flex-1")
                else:
                    ui.button("添加英雄", on_click=self.add_hero).classes("w-full")


@ui.page(DatabaseDemoApp.ROUTER)
def database_demo_page() -> None:
    """数据库演示页面."""
    app = DatabaseDemoApp()
    app.build()
