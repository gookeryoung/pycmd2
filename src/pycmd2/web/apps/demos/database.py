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
            response = await fetch("heroes")
            if response.is_success():
                heroes_data = await response.json()
                self.heroes = [Hero(**hero_data) for hero_data in heroes_data]
                ui.notify("英雄数据加载成功", type="positive")
            else:
                ui.notify(f"加载英雄数据失败: HTTP {response.status_code}", type="negative")

            # 如果API失败, 使用模拟数据作为后备
            if not self.heroes:
                self.heroes = [
                    Hero(
                        id=1,
                        name="钢铁侠",
                        description="天才发明家, 拥有高科技装甲",
                        power_level=95,
                        is_active=True,
                    ),
                    Hero(
                        id=2,
                        name="美国队长",
                        description="二战时期的超级士兵, 拥有超强体能",
                        power_level=80,
                        is_active=True,
                    ),
                    Hero(
                        id=3,
                        name="雷神",
                        description="阿斯加德的雷神, 拥有神力",
                        power_level=90,
                        is_active=False,
                    ),
                ]
                ui.notify("使用模拟数据", type="info")
        except Exception as e:
            # 如果API调用失败, 使用模拟数据
            self.heroes = [
                Hero(
                    id=1,
                    name="钢铁侠",
                    description="天才发明家, 拥有高科技装甲",
                    power_level=95,
                    is_active=True,
                ),
                Hero(
                    id=2,
                    name="美国队长",
                    description="二战时期的超级士兵, 拥有超强体能",
                    power_level=80,
                    is_active=True,
                ),
                Hero(
                    id=3,
                    name="雷神",
                    description="阿斯加德的雷神, 拥有神力",
                    power_level=90,
                    is_active=False,
                ),
            ]
            ui.notify(f"API调用失败, 使用模拟数据: {e!s}", type="info")

    async def add_hero(self) -> None:
        """添加新英雄."""
        if not self.new_hero_name:
            ui.notify("请填写英雄名称", type="warning")
            return

        try:
            # 创建英雄数据
            hero_data = Hero(
                name=self.new_hero_name,
                description=self.new_hero_description,
                power_level=self.new_hero_power_level,
                is_active=self.new_hero_is_active,
            )

            # 调用API
            response = await fetch(
                "api/heroes/",
                method="POST",
                data=hero_data.dict(),
            )

            if response.is_success():
                new_hero_data = await response.json()
                new_hero = Hero(**new_hero_data)
                self.heroes.append(new_hero)
                ui.notify("英雄添加成功", type="positive")
            else:
                ui.notify(f"添加英雄失败: HTTP {response.status_code}", type="negative")

            # 清空输入字段
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True
        except Exception as e:
            # 如果API调用失败, 模拟添加英雄
            new_hero = Hero(
                id=len(self.heroes) + 1,
                name=self.new_hero_name,
                description=self.new_hero_description,
                power_level=self.new_hero_power_level,
                is_active=self.new_hero_is_active,
            )
            self.heroes.append(new_hero)

            # 清空输入字段
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True

            ui.notify(f"API调用失败, 模拟添加成功: {e!s}", type="info")

    async def delete_hero(self, hero_id: int) -> None:
        """删除英雄."""
        try:
            # 调用API
            response = await fetch(f"api/heroes/{hero_id}", method="DELETE")

            if response.is_success():
                # 删除成功, 更新本地数据
                self.heroes = [hero for hero in self.heroes if hero.id != hero_id]
                ui.notify("英雄删除成功", type="positive")
            else:
                ui.notify(f"删除英雄失败: HTTP {response.status_code}", type="negative")
        except Exception as e:
            # 如果API调用失败, 模拟删除英雄
            self.heroes = [hero for hero in self.heroes if hero.id != hero_id]
            ui.notify(f"API调用失败, 模拟删除成功: {e!s}", type="info")

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

            # 调用API
            response = await fetch(
                f"api/heroes/{self.selected_hero.id}",
                method="PUT",
                data=hero_data.dict(exclude_unset=True),
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
                ui.notify(f"更新英雄失败: HTTP {response.status_code}", type="negative")

            # 重置表单
            self.selected_hero = None
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True
        except Exception as e:
            # 如果API调用失败, 模拟更新英雄
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

            # 重置表单
            self.selected_hero = None
            self.new_hero_name = ""
            self.new_hero_description = ""
            self.new_hero_power_level = 1
            self.new_hero_is_active = True

            ui.notify(f"API调用失败, 模拟更新成功: {e!s}", type="info")

    def render(self) -> None:
        """渲染界面."""
        ui.label("英雄管理系统").classes("text-2xl font-bold mb-4")

        # 英雄列表
        with ui.card().classes("w-full mb-4"):
            ui.label("英雄列表").classes("text-xl font-bold mb-2")
            ui.button("加载英雄", on_click=self.load_heroes).classes("mb-2")

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
