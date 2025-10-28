from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    """Model for creating a workspace."""

    name: str
    parent_path: Optional[str] = None
