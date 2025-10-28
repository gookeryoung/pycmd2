"""Local GUI application for MiniDB using tkinter."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from pycmd2.web.minidb.core import MiniDB
from pycmd2.web.minidb.core import Workspace

logger = logging.getLogger(__name__)


class MiniDBGUI:
    """MiniDB界面."""

    def __init__(self, db_path: str = "minidb.json") -> None:
        self.db = MiniDB(db_path)
        self.root = tk.Tk()
        self.root.title("MiniDB - Personal Database")
        self.root.geometry("800x600")

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.setup_ui()
        self.refresh_workspaces()

    def setup_ui(self) -> None:
        """Setup the UI."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="MiniDB Personal Database",
            font=("Arial", 16, "bold"),
        )
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Left panel - Workspaces tree
        left_frame = ttk.LabelFrame(main_frame, text="Workspaces", padding="10")
        left_frame.grid(
            row=1,
            column=0,
            sticky=(tk.W, tk.E, tk.N, tk.S),  # type: ignore
            padx=(0, 10),
        )
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Workspace controls
        workspace_controls = ttk.Frame(left_frame)
        workspace_controls.grid(
            row=0,
            column=0,
            sticky=(tk.W, tk.E),  # type: ignore
            pady=(0, 10),
        )

        ttk.Button(
            workspace_controls,
            text="New Root",
            command=self.create_root_workspace,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            workspace_controls,
            text="Refresh",
            command=self.refresh_workspaces,
        ).pack(side=tk.LEFT)

        # Workspace treeview
        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore

        tree_scrollbar = ttk.Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))  # type: ignore
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_workspace_select)

        # Right panel - Workspace details
        right_frame = ttk.LabelFrame(
            main_frame,
            text="Workspace Details",
            padding="10",
        )
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(2, weight=1)

        # Workspace info
        self.info_frame = ttk.Frame(right_frame)
        self.info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))  # type: ignore

        # Data section
        data_frame = ttk.LabelFrame(right_frame, text="Data", padding="10")
        data_frame.grid(
            row=1,
            column=0,
            sticky=(tk.W, tk.E, tk.N, tk.S),  # type: ignore
            pady=(0, 10),
        )
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(1, weight=1)

        # Data controls
        data_controls = ttk.Frame(data_frame)
        data_controls.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E),  # type: ignore
            pady=(0, 10),
        )

        ttk.Button(
            data_controls,
            text="Add Data",
            command=self.add_data_dialog,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            data_controls,
            text="Save DB",
            command=self.save_database,
        ).pack(side=tk.LEFT)

        # Data listbox
        listbox_frame = ttk.Frame(data_frame)
        listbox_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E, tk.N, tk.S),  # type: ignore
        )
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.data_listbox = tk.Listbox(listbox_frame)
        self.data_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # type: ignore

        listbox_scrollbar = ttk.Scrollbar(
            listbox_frame,
            orient=tk.VERTICAL,
            command=self.data_listbox.yview,
        )
        listbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))  # type: ignore
        self.data_listbox.configure(yscrollcommand=listbox_scrollbar.set)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
        )
        status_bar.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E),  # type: ignore
            pady=(10, 0),
        )

    def refresh_workspaces(self) -> None:
        """Refresh the workspace tree."""
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add workspaces
        for workspace in self.db.root_workspaces:
            self.add_workspace_to_tree("", workspace)

        self.status_var.set(
            f"Loaded {len(self.db.root_workspaces)} root workspaces",
        )

    def add_workspace_to_tree(self, parent: str, workspace: Workspace) -> None:
        """Add a workspace to the tree view."""
        node_id = self.tree.insert(
            parent,
            "end",
            text=workspace.name,
            values=[workspace.get_path()],
        )

        # Add children recursively
        for child in workspace.children:
            self.add_workspace_to_tree(node_id, child)

    def on_workspace_select(self, event: tk.Event) -> None:  # noqa: ARG002
        """Handle workspace selection."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        path = (
            self.tree.item(item, "values")[0]
            if self.tree.item(item, "values")
            else None
        )

        if not path:
            return

        workspace = self.db.get_workspace_by_path(path)
        if not workspace:
            return

        self.show_workspace_details(workspace)

    def show_workspace_details(self, workspace: Workspace) -> None:
        """Show workspace details."""
        # Clear previous info
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Show workspace info
        ttk.Label(
            self.info_frame,
            text=f"Name: {workspace.name}",
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.info_frame, text=f"Path: {workspace.get_path()}").grid(
            row=1,
            column=0,
            sticky=tk.W,
        )
        ttk.Label(
            self.info_frame,
            text=f"Created: {workspace.created_at}",
        ).grid(row=2, column=0, sticky=tk.W)

        # Clear and populate data listbox
        self.data_listbox.delete(0, tk.END)
        for key, value in workspace.data.items():
            self.data_listbox.insert(tk.END, f"{key}: {value}")

    def create_root_workspace(self) -> None:
        """Create a new root workspace."""
        dialog = WorkspaceDialog(self.root, "Create Root Workspace")
        name = dialog.result

        if name:
            try:
                self.db.create_workspace(name)
                self.db.save()
                self.refresh_workspaces()
                self.status_var.set(f"Created workspace: {name}")
            except Exception as e:
                logger.exception("Failed to create workspace")
                messagebox.showerror(
                    "Error",
                    f"Failed to create workspace: {e!s}",
                )

    def add_data_dialog(self) -> None:
        """Open dialog to add data to selected workspace."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workspace first")
            return

        item = selection[0]
        path = (
            self.tree.item(item, "values")[0]
            if self.tree.item(item, "values")
            else None
        )

        if not path:
            return

        workspace = self.db.get_workspace_by_path(path)
        if not workspace:
            return

        dialog = DataDialog(self.root, "Add Data")
        key, value = dialog.result

        if key and value:
            try:
                workspace.add_data(key, value)
                self.db.save()
                self.show_workspace_details(workspace)
                self.status_var.set(f"Added data to {workspace.name}")
            except Exception as e:
                logger.exception("Failed to add data")
                messagebox.showerror("Error", f"Failed to add data: {e!s}")

    def save_database(self) -> None:
        """Save the database."""
        try:
            self.db.save()
            self.status_var.set("Database saved successfully")
        except Exception as e:
            logger.exception("Failed to save database")
            messagebox.showerror("Error", f"Failed to save database: {e!s}")

    def run(self) -> None:
        """Run the GUI application."""
        self.root.mainloop()


class WorkspaceDialog:
    """Workspace creation dialog."""

    def __init__(self, parent: tk.Tk, title: str) -> None:
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("300x100")
        self.top.transient(parent)
        self.top.grab_set()

        # Center the dialog
        self.top.geometry(
            f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}",
        )

        ttk.Label(self.top, text="Workspace Name:").pack(pady=(10, 0))

        self.entry = ttk.Entry(self.top, width=30)
        self.entry.pack(pady=5)
        self.entry.focus()

        button_frame = ttk.Frame(self.top)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="OK", command=self.ok).pack(
            side=tk.LEFT,
            padx=(0, 5),
        )
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(
            side=tk.LEFT,
        )

        self.top.bind("<Return>", lambda _: self.ok())
        self.top.bind("<Escape>", lambda _: self.cancel())

        # Wait for the dialog to finish
        parent.wait_window(self.top)

    def ok(self) -> None:
        """OK button callback."""
        self.result = self.entry.get().strip()
        if self.result:
            self.top.destroy()

    def cancel(self) -> None:
        """Cancel the dialog."""
        self.top.destroy()


class DataDialog:
    """Dialog to add data to a workspace."""

    def __init__(self, parent: tk.Tk, title: str) -> None:
        self.result = (None, None)

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("300x150")
        self.top.transient(parent)
        self.top.grab_set()

        # Center the dialog
        self.top.geometry(
            f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}",
        )

        ttk.Label(self.top, text="Key:").pack(pady=(10, 0))
        self.key_entry = ttk.Entry(self.top, width=30)
        self.key_entry.pack(pady=5)
        self.key_entry.focus()

        ttk.Label(self.top, text="Value:").pack(pady=(10, 0))
        self.value_entry = ttk.Entry(self.top, width=30)
        self.value_entry.pack(pady=5)

        button_frame = ttk.Frame(self.top)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="OK", command=self.ok).pack(
            side=tk.LEFT,
            padx=(0, 5),
        )
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(
            side=tk.LEFT,
        )

        self.top.bind("<Return>", lambda _: self.ok())
        self.top.bind("<Escape>", lambda _: self.cancel())

        # Wait for the dialog to finish
        parent.wait_window(self.top)

    def ok(self) -> None:
        """OK button clicked."""
        key = self.key_entry.get().strip()
        value = self.value_entry.get().strip()
        if key and value:
            self.result = (key, value)
            self.top.destroy()

    def cancel(self) -> None:
        """Cancel the dialog."""
        self.top.destroy()


def main() -> None:
    # Run the GUI application
    app = MiniDBGUI()
    app.run()


if __name__ == "__main__":
    main()
