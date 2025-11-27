from __future__ import annotations

import asyncio
import logging
import operator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import httpx
from nicegui import ui

from pycmd2.backend.api import fetch
from pycmd2.web.component import BaseComponent

logger = logging.getLogger(__name__)


class DBTable(BaseComponent):
    """数据库表格组件, 支持对特定api_url的数据进行CRUD操作."""

    def __init__(
        self,
        api_url: str,
        columns: List[Dict[str, str]],
        *args: Tuple[Any, ...],
        **kwargs: Dict[str, Any],
    ) -> None:
        """初始化DBTable组件.

        Args:
            api_url: API端点URL
            columns: 表格列定义
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)

        self.api_url = api_url
        self.columns = columns
        self.rows: List[Dict[str, Any]] = []
        self.table_ref: Optional[ui.table] = None
        self.loading_ref: Optional[ui.spinner] = None
        self.form_dialog: Optional[ui.dialog] = None
        self.current_record: Optional[Dict[str, Any]] = None
        self.is_edit_mode = False

    def render(self) -> ui.element:
        """渲染数据库表格组件.

        Returns:
            ui.element: 数据库表格组件
        """
        with ui.element() as container:
            # 工具栏
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.label(f"数据管理 - {self.api_url}").classes("text-xl font-bold")
                with ui.row().classes("gap-2"):
                    ui.button("刷新", on_click=self.load_data, icon="refresh")
                    ui.button("添加", on_click=self.open_create_form, icon="add")

            # 加载指示器
            self.loading_ref = ui.spinner(size="lg").classes("mx-auto")
            self.loading_ref.set_visibility(False)

            # 数据表格
            self.table_ref = ui.table(
                columns=self.columns,
                rows=self.rows,
                pagination=10,
            ).classes("w-full")

            # 添加操作列
            self._add_action_column()

            # 表单对话框
            self._create_form_dialog()

        # 初始化加载数据
        asyncio.create_task(self.load_data())

        return container

    def _add_action_column(self) -> None:
        """添加操作列."""
        if self.table_ref:
            actions_column = {
                "name": "actions",
                "label": "操作",
                "field": "",
                "align": "right",
            }
            self.table_ref._props["columns"].append(actions_column)

            self.table_ref.add_slot(
                "body-cell-actions",
                """
                <q-td :props="props" class="text-right">
                    <q-btn
                        flat
                        dense
                        round
                        icon="edit"
                        @click="() => editRecord(props.row)"
                        color="primary"
                        size="sm"
                        class="mr-1"
                    />
                    <q-btn
                        flat
                        dense
                        round
                        icon="delete"
                        @click="() => deleteRecord(props.row)"
                        color="negative"
                        size="sm"
                    />
                </q-td>
            """,
            )

            # 注入JavaScript方法
            self.table_ref.on("editRecord", lambda e: self.open_edit_form(e.args))
            self.table_ref.on("deleteRecord", lambda e: self.delete_record(e.args))

    def _create_form_dialog(self) -> None:
        """创建表单对话框."""
        with ui.dialog() as self.form_dialog, ui.card().classes("w-96"):
            ui.label("编辑记录").classes("text-h6").bind_visibility_from(self, "is_edit_mode")
            ui.label("新建记录").classes("text-h6").bind_visibility_from(self, "is_edit_mode", backward=operator.not_)

            # 动态创建表单字段
            form_inputs = {}
            for col in self.columns:
                if col["name"] != "id":  # 不编辑ID字段
                    field_name = col["name"]
                    field_label = col.get("label", field_name)
                    form_inputs[field_name] = ui.input(field_label).classes("w-full")

            # 保存和取消按钮
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("取消", on_click=self.close_form).props("flat")
                ui.button("保存", on_click=lambda: self.save_record(form_inputs)).props("color=primary")

    async def load_data(self) -> None:
        """从API加载数据."""
        if self.loading_ref:
            self.loading_ref.set_visibility(True)

        try:
            logger.info(f"加载数据: {self.api_url}")
            response = await fetch(self.api_url)
            if response.is_success():
                self.rows[:] = await response.json()
                if self.table_ref:
                    self.table_ref.update()

                ui.notify(f"数据加载成功: {self.rows}", type="positive")
            else:
                ui.notify(f"加载数据失败: {response.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"加载数据时出错: {e!s}", type="negative")
        finally:
            if self.loading_ref:
                self.loading_ref.set_visibility(False)

    def open_create_form(self) -> None:
        """打开创建记录表单."""
        self.is_edit_mode = False
        self.current_record = {}
        if self.form_dialog:
            self.form_dialog.open()

    def open_edit_form(self, record: Dict[str, Any]) -> None:
        """打开编辑记录表单."""
        self.is_edit_mode = True
        self.current_record = record.copy()
        if self.form_dialog:
            self.form_dialog.open()

    def close_form(self) -> None:
        """关闭表单."""
        if self.form_dialog:
            self.form_dialog.close()

    async def save_record(self, form_inputs: Dict[str, ui.input]) -> None:
        """保存记录."""
        # 收集表单数据
        record_data = {}
        for field_name, input_element in form_inputs.items():
            record_data[field_name] = input_element.value

        try:
            async with httpx.AsyncClient() as client:
                if self.is_edit_mode and self.current_record and "id" in self.current_record:
                    # 更新记录
                    record_id = self.current_record["id"]
                    response = await client.put(f"{self.api_url}/{record_id}", json=record_data)
                else:
                    # 创建记录
                    response = await client.post(self.api_url, json=record_data)

                if response.status_code in {200, 201}:
                    ui.notify("记录保存成功", type="positive")
                    self.close_form()
                    await self.load_data()  # 重新加载数据
                else:
                    ui.notify(f"保存记录失败: {response.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"保存记录时出错: {e!s}", type="negative")

    async def delete_record(self, record: Dict[str, Any]) -> None:
        """删除记录."""
        if "id" not in record:
            ui.notify("无法删除记录：缺少ID", type="negative")
            return

        confirm = await ui.dialog.confirm(f"确定要删除记录 #{record['id']} 吗?").result
        if not confirm:
            return

        try:
            async with httpx.AsyncClient() as client:
                record_id = record["id"]
                response = await client.delete(f"{self.api_url}/{record_id}")

                if response.status_code == 200:
                    ui.notify("记录删除成功", type="positive")
                    await self.load_data()  # 重新加载数据
                elif response.status_code == 204:  # No Content
                    ui.notify("记录删除成功", type="positive")
                    await self.load_data()
                else:
                    ui.notify(f"删除记录失败: {response.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"删除记录时出错: {e!s}", type="negative")
