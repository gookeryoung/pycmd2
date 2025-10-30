from __future__ import annotations

from typing import Dict
from typing import List

from fastapi import APIRouter

router = APIRouter()


@router.get("/users/", tags=["users"])
async def list_users() -> List[Dict[str, str]]:
    return [{"username": "Rick"}, {"username": "Mark"}]
