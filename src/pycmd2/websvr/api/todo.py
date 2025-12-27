"""FastAPI后端服务器 - 为Todo应用提供RESTful API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List
from typing import Optional

import trio
import typer
from fastapi import HTTPException
from fastapi import status
from fastapi.routing import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/todos",
    tags=["todos"],
    responses={404: {"description": "待办事项不存在"}},
)

DATA_DIR = Path.home() / ".pycmd2" / "websvr"
DATA_DIR.mkdir(exist_ok=True)
TODOS_FILE = DATA_DIR / "todos.json"


# 数据模型
class Todo(BaseModel):
    """待办事项数据模型."""

    id: int
    text: str
    completed: bool
    created_at: str


class TodoCreate(BaseModel):
    """待办事项创建数据模型."""

    text: str


class TodoUpdate(BaseModel):
    """待办事项更新数据模型."""

    text: Optional[str] = None
    completed: Optional[bool] = None


class TodoList(BaseModel):
    """待办事项列表数据模型."""

    todos: List[Todo]


# 数据操作函数
def load_todos() -> List[Todo]:
    """从文件加载待办事项."""
    if not TODOS_FILE.exists():
        typer.echo("未找到待办事项文件")
        return []

    try:
        with TODOS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [Todo(**todo) for todo in data]
            if isinstance(data, dict) and "todos" in data:
                return [Todo(**todo) for todo in data["todos"]]
            return []
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def save_todos(todos: List[Todo]) -> bool:
    """保存待办事项到文件."""
    try:
        # 确保目录存在
        TODOS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 保存为JSON格式
        data = [todo.model_dump() for todo in todos]
        with TODOS_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        return False
    else:
        return True


def get_next_id(todos: List[Todo]) -> int:
    """获取下一个可用的ID."""
    if not todos:
        return 1
    return max(todo.id for todo in todos) + 1


@router.get("/", response_model=List[Todo])
def get_todos() -> List[Todo]:
    """获取所有待办事项."""
    return load_todos()


@router.post("/", response_model=Todo)
def create_todo(todo_data: TodoCreate) -> Todo:
    """创建新的待办事项."""
    todos = load_todos()

    new_todo = Todo(
        id=get_next_id(todos),
        text=todo_data.text.strip(),
        completed=False,
        created_at=str(trio.Path(__file__).stat),  # 简化的时间戳
    )

    todos.append(new_todo)

    if save_todos(todos):
        return new_todo
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="保存待办事项失败",
    )


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: int) -> Todo:
    """获取指定ID的待办事项."""
    todos = load_todos()
    todo = next((t for t in todos if t.id == todo_id), None)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"待办事项 {todo_id} 不存在",
        )

    return todo


@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate) -> Todo:
    """更新待办事项."""
    todos = load_todos()
    todo = next((t for t in todos if t.id == todo_id), None)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"待办事项 {todo_id} 不存在",
        )

    # 更新字段
    if todo_update.text is not None:
        todo.text = todo_update.text.strip()
    if todo_update.completed is not None:
        todo.completed = todo_update.completed

    # 保存更新
    if save_todos(todos):
        return todo
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="更新待办事项失败",
    )


@router.delete("/{todo_id}")
def delete_todo(todo_id: int) -> dict:
    """删除待办事项."""
    todos = load_todos()
    original_length = len(todos)

    todos = [t for t in todos if t.id != todo_id]

    if len(todos) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"待办事项 {todo_id} 不存在",
        )

    if save_todos(todos):
        return {"message": f"待办事项 {todo_id} 已删除"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="删除待办事项失败",
    )


@router.delete("/")
def clear_completed() -> dict:
    """清除已完成的待办事项."""
    todos = load_todos()
    completed_count = len([t for t in todos if t.completed])

    if completed_count == 0:
        return {"message": "没有已完成的待办事项需要清除"}

    todos = [t for t in todos if not t.completed]

    if save_todos(todos):
        return {"message": f"已清除 {completed_count} 个已完成的待办事项"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="清除已完成待办事项失败",
    )


@router.delete("/all")
def clear_all() -> dict:
    """清除所有待办事项."""
    if save_todos([]):
        return {"message": "所有待办事项已清除"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="清除所有待办事项失败",
    )


@router.get("/stats")
def get_stats() -> dict:
    """获取待办事项统计信息."""
    todos = load_todos()
    total = len(todos)
    completed = len([t for t in todos if t.completed])
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 2),
    }


@router.post("/import")
def import_todos(todo_list: TodoList) -> dict:
    """导入待办事项列表."""
    todos = load_todos()

    # 合并导入的数据
    max_id = max([t.id for t in todos], default=0)

    for imported_todo in todo_list.todos:
        # 确保ID唯一
        if imported_todo.id <= max_id:
            max_id += 1
            imported_todo.id = max_id

        # 检查是否已存在相同ID的项目
        existing = next((t for t in todos if t.id == imported_todo.id), None)
        if not existing:
            todos.append(imported_todo)

    if save_todos(todos):
        return {"message": f"成功导入 {len(todo_list.todos)} 个待办事项"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="导入待办事项失败",
    )


@router.get("/export")
def export_todos() -> dict:
    """导出所有待办事项."""
    todos = load_todos()
    return {"todos": [todo.model_dump() for todo in todos]}
