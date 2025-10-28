"""Minidb core module - Personal database with workspace hierarchy support."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

logger = logging.getLogger(__name__)


class Workspace:
    """Represents a workspace in the personal database, Workspaces can have hierarchical structure."""  # noqa: E501

    def __init__(self, name: str, parent: Workspace | None = None) -> None:
        self.name = name
        self.parent = parent
        self.children: List[Workspace] = []
        self.data: Dict[str, Any] = {}
        self.created_at = datetime.now(timezone.utc)

        if parent:
            parent.add_child(self)

    def add_child(self, child: Workspace) -> None:
        """Add a child workspace."""
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child: Workspace) -> None:
        """Remove a child workspace."""
        if child in self.children:
            self.children.remove(child)

    def get_path(self) -> str:
        """Get the full path of the workspace.

        Returns:
            str: The full path of the workspace.
        """
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return self.name

    def add_data(self, key: str, value: object) -> None:
        """Add data to the workspace."""
        self.data[key] = value

    def get_data(self, key: str) -> object:
        """Get data from the workspace.

        Returns:
            object: The data value or None if not found.
        """
        return self.data.get(key)

    def remove_data(self, key: str) -> None:
        """Remove data from the workspace."""
        if key in self.data:
            del self.data[key]


class MiniDB:
    """Main personal database class that manages workspaces."""

    def __init__(self, db_path: str = "minidb.json") -> None:
        self.db_path = db_path
        self.root_workspaces: List[Workspace] = []
        self.load()

    def create_workspace(
        self,
        name: str,
        parent: Workspace | None = None,
    ) -> Workspace:
        """Create a new workspace.

        Returns:
            Workspace: The created workspace.
        """
        workspace = Workspace(name, parent)
        if not parent:
            self.root_workspaces.append(workspace)
        return workspace

    def get_workspace_by_path(self, path: str) -> Workspace | None:
        """Get a workspace by its path.

        Returns:
            Workspace | None: The workspace or None if not found.
        """
        parts = path.strip("/").split("/")
        if not parts or not parts[0]:
            return None

        # Find root workspace
        root_name = parts[0]
        root_ws = None
        for ws in self.root_workspaces:
            if ws.name == root_name:
                root_ws = ws
                break

        if not root_ws:
            return None

        if len(parts) == 1:
            return root_ws

        # Traverse children
        current_ws = root_ws
        for part in parts[1:]:
            found = False
            for child in current_ws.children:
                if child.name == part:
                    current_ws = child
                    found = True
                    break
            if not found:
                return None

        return current_ws

    def delete_workspace(self, path: str) -> bool:
        """Delete a workspace by its path.

        Returns:
            bool: True if the workspace was deleted, False otherwise.
        """
        workspace = self.get_workspace_by_path(path)
        if not workspace:
            return False

        if workspace.parent:
            workspace.parent.remove_child(workspace)
        # Root workspace
        elif workspace in self.root_workspaces:
            self.root_workspaces.remove(workspace)
        return True

    def save(self) -> None:
        """Save the database to file."""
        data = {
            "root_workspaces": [
                self._serialize_workspace(ws) for ws in self.root_workspaces
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Create directory if not exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with Path(self.db_path).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def load(self) -> None:
        """Load the database from file."""
        if not Path(self.db_path).exists():
            return

        try:
            with Path(self.db_path).open(encoding="utf-8") as f:
                data = json.load(f)

            self.root_workspaces = [
                self._deserialize_workspace(ws_data)
                for ws_data in data.get("root_workspaces", [])
            ]
        except FileNotFoundError:
            logger.exception("Failed to load database")

    def _serialize_workspace(self, workspace: Workspace) -> Dict[str, Any]:
        """Serialize a workspace to dictionary.

        Returns:
            Dict[str, Any]: Serialized workspace.
        """
        return {
            "name": workspace.name,
            "data": workspace.data,
            "children": [
                self._serialize_workspace(child) for child in workspace.children
            ],
            "created_at": workspace.created_at.isoformat()
            if hasattr(workspace.created_at, "isoformat")
            else str(workspace.created_at),
        }

    def _deserialize_workspace(
        self,
        data: Dict[str, Any],
        parent: Workspace | None = None,
    ) -> Workspace:
        """Deserialize a workspace from dictionary.

        Returns:
            Workspace: Deserialized workspace.
        """
        workspace = Workspace(data["name"], parent)
        workspace.data = data.get("data", {})

        # Parse created_at if present
        if "created_at" in data:
            try:
                workspace.created_at = datetime.fromisoformat(
                    data["created_at"],
                )
            except ValueError:
                logger.warning(
                    f"Invalid created_at value: {data['created_at']}",
                )

        # Deserialize children
        for child_data in data.get("children", []):
            self._deserialize_workspace(child_data, workspace)

        return workspace
