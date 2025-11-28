from __future__ import annotations

import asyncio
import logging
import operator
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from nicegui import ui

from pycmd2.backend.api import fetch
from pycmd2.web.component import BaseComponent

logger = logging.getLogger(__name__)


@dataclass
class DBTableColumn:
    """数据库表格列定义.

    Attributes:
        name: 列名
        label: 列标题
        field: 字段名

    Examples:
        >>> col = DBTableColumn(name="id", label="ID", field="id")
        >>> col
        DBTableColumn(name="id", label="ID", field="id")
    """

    name: str
    label: str
    field: str

    def __repr__(self) -> str:
        """转换为字符串.

        Returns:
            str: 表格列定义字符串
        """
        return f'DBTableColumn(name="{self.name}", label="{self.label}", field="{self.field}")'

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式.

        Returns:
            Dict[str, Any]: 列配置字典
        """
        return {
            "name": self.name,
            "label": self.label,
            "field": self.field,
        }


class DBTable(BaseComponent):
    """数据库表格组件, 支持对特定api_url的数据进行CRUD操作.

    Attributes:
        api_url: API端点URL
        columns: 表格列定义, 可以是DBTableColumn对象列表或字典列表

    Examples:
        >>> columns = [
        ...     DBTableColumn(name="id", label="ID", field="id"),
        ...     DBTableColumn(name="name", label="名称", field="name"),
        ... ]
        >>> table = DBTable(api_url="/api/users/", columns=columns)
        >>> table
        DBTable(api_url="/api/users/", columns=[DBTableColumn(name="id", label="ID", field="id"), DBTableColumn(name="name", label="名称", field="name")])
        >>> table.converted_columns
        [{'name': 'id', 'label': 'ID', 'field': 'id'}, {'name': 'name', 'label': '名称', 'field': 'name'}]
        >>> isinstance(table.render(), ui.element)
        True
    """  # noqa: E501

    def __init__(
        self,
        api_url: str,
        columns: List[DBTableColumn],
        *args: tuple[Any, ...],
        **kwargs: Dict[str, Any],
    ) -> None:
        """初始化DBTable组件.

        Args:
            api_url: API端点URL
            columns: 表格列定义, 可以是DBTableColumn对象列表或字典列表
            *args: 剩余参数
            **kwargs: 剩余参数
        """
        super().__init__(*args, **kwargs)

        self.api_url = api_url if api_url.endswith("/") else f"{api_url}/"

        # 确保列是字典格式
        self.columns = columns
        self.rows: List[Dict[str, Any]] = []
        self.table_ref: Optional[ui.table] = None
        self.loading_ref: Optional[ui.spinner] = None
        self.form_dialog: Optional[ui.dialog] = None
        self.current_record: Optional[Dict[str, Any]] = None
        self.is_edit_mode = False
        self._tasks = set()  # 用于保存任务引用, 避免被垃圾回收

    def __repr__(self) -> str:
        """转换为字符串.

        Returns:
            str: 表格组件字符串
        """
        return f'DBTable(api_url="{self.api_url}", columns={self.columns})'

    @property
    def converted_columns(self) -> List[Dict[str, Any]]:
        """转换列定义为字典格式.

        Returns:
            List[Dict[str, Any]]: 列定义字典列表
        """
        return [col.to_dict() for col in self.columns]

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
                columns=self.converted_columns,
                rows=self.rows,
                pagination=10,
            ).classes("w-full")

            # 添加操作列
            self._add_action_column()

            # 表单对话框
            self._create_form_dialog()

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

            with self.table_ref.add_slot("body-cell-actions"):

                def render_actions(props) -> None:
                    with ui.row().classes("gap-1"):
                        ui.button(
                            icon="edit",
                            on_click=lambda e, r=props.row: self.open_edit_form(r),
                        ).props("flat dense color=primary size=sm")
                        ui.button(
                            icon="delete",
                            on_click=lambda e, r=props.row: self.delete_record(r),
                        ).props("flat dense color=negative size=sm")

    def _create_form_dialog(self) -> None:
        """创建表单对话框."""
        with ui.dialog() as self.form_dialog, ui.card().classes("w-96"):
            ui.label("编辑记录").classes("text-h6").bind_visibility_from(self, "is_edit_mode")
            ui.label("新建记录").classes("text-h6").bind_visibility_from(self, "is_edit_mode", backward=operator.not_)

            # 动态创建表单字段
            self.form_inputs = {}
            for col in self.columns:
                if col.name != "id":  # 不编辑ID字段
                    field_name = col.name
                    field_label = col.label or col.field
                    input_field = ui.input(field_label).classes("w-full")
                    self.form_inputs[field_name] = input_field

            # 保存和取消按钮
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("取消", on_click=self.close_form).props("flat")
                ui.button("保存", on_click=lambda: self.save_record(self.form_inputs)).props("color=primary")

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

                logger.info(f"数据加载成功: {self.rows}")
            else:
                logger.error(f"加载数据失败: {response.status_code}")
        except Exception:
            logger.exception("加载数据时出错")
        finally:
            if self.loading_ref:
                self.loading_ref.set_visibility(False)

    def after_render(self) -> None:
        """组件渲染后执行."""
        task = asyncio.create_task(self.load_data())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    def open_create_form(self) -> None:
        """打开创建记录表单."""
        self.is_edit_mode = False
        self.current_record = {}

        # 清空表单字段
        if hasattr(self, "form_inputs"):
            for input_field in self.form_inputs.values():
                input_field.value = ""

        if self.form_dialog:
            self.form_dialog.open()

    def open_edit_form(self, record: Dict[str, Any]) -> None:
        """打开编辑记录表单."""
        self.is_edit_mode = True
        self.current_record = record.copy()

        # 填充表单字段
        if hasattr(self, "form_inputs"):
            for field_name, input_field in self.form_inputs.items():
                if field_name in self.current_record:
                    input_field.value = str(self.current_record[field_name])

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
            if self.is_edit_mode and self.current_record and "id" in self.current_record:
                # 更新记录 - 使用PATCH方法以匹配API路由
                record_id = self.current_record["id"]
                response = await fetch(f"{self.api_url}/{record_id}", method="PATCH", data=record_data)
            else:
                # 创建记录 - 使用POST方法
                response = await fetch(self.api_url, method="POST", data=record_data)

            if response.is_success():
                ui.notify("记录保存成功", type="positive")
                self.close_form()
                await self.load_data()  # 重新加载数据
            else:
                error_text = await response.text()
                ui.notify(f"保存记录失败: {response.status_code} - {error_text}", type="negative")
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
            # 使用fetch函数删除记录
            record_id = record["id"]
            response = await fetch(f"{self.api_url}/{record_id}", method="DELETE")

            if response.is_success():
                ui.notify("记录删除成功", type="positive")
                await self.load_data()  # 重新加载数据
            else:
                error_text = await response.text()
                ui.notify(f"删除记录失败: {response.status_code} - {error_text}", type="negative")
        except Exception as e:
            ui.notify(f"删除记录时出错: {e!s}", type="negative")
