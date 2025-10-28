"""CLI interface for MiniDB."""

from __future__ import annotations

import argparse
import logging
import sys

import click

from pycmd2.web.minidb.core import MiniDB
from pycmd2.web.minidb.web_api import create_app as create_flask_app


@click.group()
def minidb() -> None:
    """MiniDB - A personal database with workspace hierarchy support."""


@minidb.command()
@click.option(
    "--db-path",
    default="minidb.json",
    help="Path to the database file",
)
def flask(db_path: str) -> None:
    """Run MiniDB web API server with Flask."""
    app = create_flask_app(db_path)
    app.run(host="127.0.0.1", port=5000, debug=True)


@minidb.command()
@click.option(
    "--db-path",
    default="minidb.json",
    help="Path to the database file",
)
def fastapi(db_path: str) -> None:
    """Run MiniDB web API server with FastAPI."""
    try:
        import uvicorn

        from pycmd2.web.minidb.app import create_app
    except ImportError as e:
        click.echo(f"Error: Required dependencies not installed: {e}")
        click.echo("Please install fastapi and uvicorn to use this feature:")
        click.echo("  pip install fastapi uvicorn[standard]")
        return

    app = create_app(db_path)
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="MiniDB - Personal Database")
    parser.add_argument(
        "--db-path",
        default="minidb.json",
        help="Path to the database file",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )

    # Create workspace command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new workspace",
    )
    create_parser.add_argument("name", help="Name of the workspace")
    create_parser.add_argument("--parent", help="Parent workspace path")

    # List workspaces command
    subparsers.add_parser("list", help="List all workspaces")

    # Delete workspace command
    delete_parser = subparsers.add_parser("delete", help="Delete a workspace")
    delete_parser.add_argument("path", help="Path of the workspace to delete")

    # Add data command
    add_parser = subparsers.add_parser(
        "add-data",
        help="Add data to a workspace",
    )
    add_parser.add_argument("path", help="Path of the workspace")
    add_parser.add_argument("key", help="Data key")
    add_parser.add_argument("value", help="Data value")

    # Get data command
    get_parser = subparsers.add_parser(
        "get-data",
        help="Get data from a workspace",
    )
    get_parser.add_argument("path", help="Path of the workspace")
    get_parser.add_argument("key", help="Data key")

    # Show workspace command
    show_parser = subparsers.add_parser("show", help="Show workspace details")
    show_parser.add_argument("path", help="Path of the workspace")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = MiniDB(args.db_path)

    try:
        if args.command == "create":
            handle_create(db, args.name, args.parent)
        elif args.command == "list":
            handle_list(db)
        elif args.command == "delete":
            handle_delete(db, args.path)
        elif args.command == "add-data":
            handle_add_data(db, args.path, args.key, args.value)
        elif args.command == "get-data":
            handle_get_data(db, args.path, args.key)
        elif args.command == "show":
            handle_show(db, args.path)
    except Exception:
        logger.exception("Error!")
        sys.exit(1)


def handle_create(
    db: MiniDB,
    name: str,
    parent_path: str | None = None,
) -> None:
    """Handle create workspace command."""
    parent = None
    if parent_path:
        parent = db.get_workspace_by_path(parent_path)
        if not parent:
            logger.error(f"Error: Parent workspace '{parent_path}' not found")
            sys.exit(1)

    workspace = db.create_workspace(name, parent)
    db.save()
    logger.info(
        f"Created workspace '{workspace.name}' "
        f"at path '{workspace.get_path()}'",
    )


def handle_list(db: MiniDB) -> None:
    """Handle list workspaces command."""

    def print_workspace(workspace: Workspace, indent: int = 0) -> None:
        prefix = "  " * indent
        data_count = len(workspace.data)
        children_count = len(workspace.children)
        info = []
        if data_count > 0:
            info.append(f"{data_count} data items")
        if children_count > 0:
            info.append(f"{children_count} children")

        info_str = f" ({', '.join(info)})" if info else ""
        logger.info(f"{prefix}- {workspace.name}{info_str}")

        for child in workspace.children:
            print_workspace(child, indent + 1)

    if not db.root_workspaces:
        logger.warning("No workspaces found")
        return

    logger.info("Workspaces:")
    for workspace in db.root_workspaces:
        print_workspace(workspace)


def handle_delete(db: MiniDB, path: str) -> None:
    """Handle delete workspace command."""
    if db.delete_workspace(path):
        db.save()
        logger.info(f"Deleted workspace '{path}'")
    else:
        logger.error(f"Error: Workspace '{path}' not found")
        sys.exit(1)


def handle_add_data(db: MiniDB, path: str, key: str, value: str) -> None:
    """Handle add data command."""
    workspace = db.get_workspace_by_path(path)
    if not workspace:
        logger.error(f"Error: Workspace '{path}' not found")
        sys.exit(1)

    workspace.add_data(key, value)
    db.save()
    logger.info(f"Added data '{key}' to workspace '{path}'")


def handle_get_data(db: MiniDB, path: str, key: str) -> None:
    """Handle get data command."""
    workspace = db.get_workspace_by_path(path)
    if not workspace:
        logger.error(f"Error: Workspace '{path}' not found")
        sys.exit(1)

    value = workspace.get_data(key)
    if value is None:
        logger.info(f"Data '{key}' not found in workspace '{path}'")
        sys.exit(1)

    logger.info(value)


def handle_show(db: MiniDB, path: str) -> None:
    """Handle show workspace command."""
    workspace = db.get_workspace_by_path(path)
    if not workspace:
        logger.error(f"Error: Workspace '{path}' not found")
        sys.exit(1)

    logger.info(f"Workspace: {workspace.name}")
    logger.info(f"Path: {workspace.get_path()}")
    logger.info(f"Created: {workspace.created_at}")

    if workspace.data:
        logger.info("Data:")
        for key, value in workspace.data.items():
            logger.info(f"  {key}: {value}")
    else:
        logger.info("No data")


if __name__ == "__main__":
    main()
