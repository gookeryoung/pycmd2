from __future__ import annotations

from typing import List

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from sqlmodel import Field
from sqlmodel import select
from sqlmodel import SQLModel
from typing_extensions import Annotated

from pycmd2.backend.database import SessionDep

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "用户不存在"}},
)

_max_name_length = 50
_max_email_length = 100


class UserBase(SQLModel):
    """用户基础模型."""

    name: str = Field(index=True, nullable=False)
    email: str = Field(nullable=True, default="")


class User(UserBase, table=True):
    """用户数据库模型."""

    id: int = Field(primary_key=True)


class UserCreate(UserBase):
    """创建用户信息."""


class UserPublic(UserBase):
    """公开用户信息."""

    id: int


@router.post("/")
def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
    """创建用户.

    Args:
        user: 用户创建信息
        session: 数据库会话依赖

    Returns:
        UserPublic: 创建的用户信息.

    Raises:
        HTTPException: 如果用户输入有误则抛出400异常.
    """

    def _validate_user_input() -> None:
        # 验证用户输入，防止恶意数据
        if not user.name or len(user.name.strip()) == 0:
            raise HTTPException(status_code=400, detail="用户名不能为空")

        if len(user.name) > _max_name_length:
            raise HTTPException(status_code=400, detail="用户名长度不能超过50个字符")

        if user.email and len(user.email) > _max_email_length:
            raise HTTPException(status_code=400, detail="邮箱长度不能超过100个字符")

    try:
        _validate_user_input()

        # 清理用户输入，去除前后空格
        user_data = user.model_dump()
        user_data["name"] = user_data["name"].strip()
        if user_data.get("email"):
            user_data["email"] = user_data["email"].strip()

        user_db = User(**user_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        return UserPublic.model_validate(user_db)
    except HTTPException:
        raise  # 重新抛出HTTPException
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(ge=0, le=100)] = 100,
) -> List[UserPublic]:
    """获取所有用户.

    Args:
        session: 数据库会话依赖
        offset: 偏移量
        limit: 限制数量

    Returns:
        List[UserPublic]: 所有用户信息.
    """
    # 确保offset和limit是有效值，防止SQL注入
    validated_offset = max(0, offset)
    validated_limit = min(100, max(0, limit))

    users = session.exec(
        select(User).offset(validated_offset).limit(validated_limit),
    ).all()
    return [UserPublic.model_validate(user) for user in users]


@router.get("/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserPublic:
    """获取单个用户.

    Args:
        user_id: 用户ID
        session: 数据库会话依赖

    Returns:
        UserPublic: 用户信息.

    Raises:
        HTTPException: 如果用户不存在则抛出404异常.
    """
    # 验证user_id，防止非法ID
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="无效的用户ID")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserPublic.model_validate(user)


@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep) -> None:
    """删除用户.

    Args:
        user_id: 用户ID
        session: 数据库会话依赖

    Raises:
        HTTPException: 如果用户不存在则抛出404异常.
    """
    # 验证user_id，防止非法ID
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="无效的用户ID")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    session.delete(user)
    session.commit()
