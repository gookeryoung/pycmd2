from fastapi import APIRouter

from pycmd2.web.minidb.core import SessionDep
from pycmd2.web.minidb.models.workspace import Workspace
from pycmd2.web.minidb.models.workspace import WorkspaceBase
from pycmd2.web.minidb.models.workspace import WorkspaceCreate

router = APIRouter()


@router.post("/api/workspaces-db-ex")
def create_workspaces_db(
    workspace: WorkspaceCreate,
    session: SessionDep,
) -> WorkspaceBase:
    """创建 workspace."""
    db_workspace = Workspace.model_validate(workspace)
    session.add(db_workspace)
    session.commit()
    session.refresh(db_workspace)
    return db_workspace
