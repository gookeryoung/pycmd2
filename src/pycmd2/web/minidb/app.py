"""FastAPI implementation for MiniDB - Allows accessing the personal database through HTTP."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any
from typing import Dict
from typing import List

import anyio
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_offline import FastAPIOffline
from pydantic import BaseModel

from pycmd2.config import TomlConfigMixin
from pycmd2.web.minidb.core import MiniDB
from pycmd2.web.minidb.models.workspace import WorkspaceCreate


class MiniDBConfig(TomlConfigMixin):
    """Configuration for MiniDB."""

    db_path: str = "minidb.json"


conf = MiniDBConfig()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPIOffline(
    title="MiniDB API",
    description="Personal database with workspace hierarchy support",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MiniDB instance
db = MiniDB(conf.db_path)


class DataAdd(BaseModel):
    """Model for adding data to a workspace."""

    key: str
    value: Any


class MessageResponse(BaseModel):
    """Model for simple message response."""

    message: str


class WorkspaceInfo(BaseModel):
    """Model for workspace info."""

    name: str
    path: str
    has_children: bool
    data_count: int


class WorkspaceDetail(WorkspaceInfo):
    """Model for detailed workspace info."""

    data: Dict[str, Any]
    children: List[WorkspaceInfo]
    created_at: str


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint.

    Returns:
        A message indicating the root endpoint.
    """
    return {"message": "Welcome to MiniDB API"}


@app.get("/api/users/me")
async def read_users_me() -> Dict[str, str]:
    """Read the current user.

    Returns:
        A message indicating the current user.
    """
    return {"username": "the current user"}


@app.get("/api/users/{user_id}")
async def read_user(user_id: str) -> Dict[str, str]:
    """Read a specific user.

    Args:
        user_id: ID of the user.

    Returns:
        A message indicating the user.
    """
    return {"username": user_id}


class ModelName(str, Enum):
    """Model name enum."""

    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/api/models/{model_name}")
async def get_model(model_name: ModelName) -> Dict[str, str]:
    """Get a specific model.

    Args:
        model_name: Name of the model.

    Returns:
        A message indicating the model.
    """
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {
            "model_name": model_name,
            "message": "Can you really beat MNIST?",
        }

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str) -> Dict[str, str]:
    """Read a file.

    Returns:
        A message indicating the file.

    Raises:
        HTTPException: If the file is not found.
    """
    filepath = anyio.Path(file_path)
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    content = await filepath.read_text(encoding="utf-8")
    return {"file_path": content}


@app.get("/api/workspaces")
async def list_root_workspaces() -> List[WorkspaceInfo]:
    """List all root workspaces.

    Returns:
        A list of workspaces.
    """
    return [
        WorkspaceInfo(
            name=ws.name,
            path=ws.get_path(),
            has_children=len(ws.children) > 0,
            data_count=len(ws.data),
        )
        for ws in db.root_workspaces
    ]


@app.get("/api/workspaces/{workspace_path:path}")
async def get_workspace(workspace_path: str) -> WorkspaceDetail:
    """Get a specific workspace by path.

    Args:
        workspace_path: Path to the workspace.

    Returns:
        Workspace details.

    Raises:
        HTTPException: If the workspace is not found.
    """
    workspace = db.get_workspace_by_path(workspace_path)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    children_info = [
        WorkspaceInfo(
            name=child.name,
            path=child.get_path(),
            has_children=len(child.children) > 0,
            data_count=len(child.data),
        )
        for child in workspace.children
    ]

    return WorkspaceDetail(
        name=workspace.name,
        path=workspace.get_path(),
        has_children=len(workspace.children) > 0,
        data_count=len(workspace.data),
        data=workspace.data,
        children=children_info,
        created_at=workspace.created_at.isoformat()
        if hasattr(workspace.created_at, "isoformat")
        else str(workspace.created_at),
    )


@app.post("/api/workspaces", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_create: WorkspaceCreate,
) -> Dict[str, str]:
    """Create a new workspace.

    Returns:
        Created workspace info.

    Raises:
        HTTPException: If the workspace creation fails.
    """
    name = workspace_create.name
    parent_path = workspace_create.parent_path

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required",
        )

    parent = None
    if parent_path:
        parent = db.get_workspace_by_path(parent_path)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent workspace not found",
            )

    try:
        workspace = db.create_workspace(name, parent)
        db.save()
        return {"name": workspace.name, "path": workspace.get_path()}
    except Exception as e:
        logger.exception("Failed to create workspace")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@app.delete("/api/workspaces/{workspace_path:path}")
async def delete_workspace(workspace_path: str) -> MessageResponse:
    """Delete a workspace by path.

    Returns:
        Success message.

    Raises:
        HTTPException: If the workspace is not found.
    """
    if db.delete_workspace(workspace_path):
        db.save()
        return MessageResponse(message="Workspace deleted successfully")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Workspace not found",
    )


@app.post("/api/workspaces/{workspace_path:path}/data")
async def add_data(
    workspace_path: str,
    data_add: DataAdd,
) -> MessageResponse:
    """Add data to a workspace.

    Returns:
        Success message.

    Raises:
        HTTPException: If the workspace is not found.
    """
    workspace = db.get_workspace_by_path(workspace_path)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    key = data_add.key
    value = data_add.value

    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key is required",
        )

    try:
        workspace.add_data(key, value)
        db.save()
        return MessageResponse(message="Data added successfully")
    except Exception as e:
        logger.exception("Failed to add data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@app.delete("/api/workspaces/{workspace_path:path}/data/{key}")
async def remove_data(workspace_path: str, key: str) -> MessageResponse:
    """Remove data from a workspace.

    Returns:
        Success message.

    Raises:
        HTTPException: If the workspace is not found.
    """
    workspace = db.get_workspace_by_path(workspace_path)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    try:
        workspace.remove_data(key)
        db.save()
        return MessageResponse(message="Data removed successfully")
    except Exception as e:
        logger.exception("Failed to remove data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@app.post("/api/save")
async def save_db() -> MessageResponse:
    """Force save the database.

    Returns:
        Success message.

    Raises:
        HTTPException: If the save fails.
    """
    try:
        db.save()
        return MessageResponse(message="Database saved successfully")
    except Exception as e:
        logger.exception("Failed to save database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


def main() -> None:
    """Run development server."""
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
