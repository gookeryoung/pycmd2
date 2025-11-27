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

    Returns:
        UserPublic: 创建的用户信息.

    Raises:
        HTTPException: 如果创建失败则抛出400异常.
    """
    try:
        user_db = User(**user.model_dump())
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        return UserPublic.model_validate(user_db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(ge=0, le=100)] = 100,
) -> List[UserPublic]:
    """获取所有用户.

    Returns:
        List[UserPublic]: 所有用户信息.
    """
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return [UserPublic.model_validate(user) for user in users]


@router.get("/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserPublic:
    """获取单个用户.

    Returns:
        UserPublic: 用户信息.

    Raises:
        HTTPException: 如果用户不存在则抛出404异常.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserPublic.model_validate(user)


@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep) -> None:
    """删除用户.

    Raises:
        HTTPException: 如果用户不存在则抛出404异常.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    session.delete(user)
    session.commit()
