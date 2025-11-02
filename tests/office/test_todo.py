from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Generator

import pytest
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot

from pycmd2.office.todo.config import conf
from pycmd2.office.todo.controller import TodoController
from pycmd2.office.todo.model import TodoItem
from pycmd2.office.todo.model import TodoListModel


class TestTodoItem:
    """Test TodoItem."""

    @pytest.mark.parametrize(
        ("text", "completed", "priority", "category"),
        [
            ("测试1", False, 0, ""),
            ("测试2", True, 1, "工作"),
            ("测试3", True, 2, "工作"),
            ("测试4", True, 3, "工作"),
        ],
    )
    def test_to_dict(
        self,
        text: str,
        *,
        completed: bool,
        priority: int,
        category: str,
    ) -> None:
        """测试TodoItem转换为字典."""
        item = TodoItem(
            text=text,
            completed=completed,
            priority=priority,
            category=category,
        )

        assert item.to_dict() == {
            "text": text,
            "completed": completed,
            "created_at": item.created_at.isoformat(),
            "completed_at": "",
            "priority": priority,
            "category": category,
        }

    def test_from_dict(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test from dict."""
        item = TodoItem.from_dict(
            {
                "text": "test",
                "completed": True,
                "created_at": "2023-01-01T00:00:00",
                "completed_at": "2023-01-01T00:00:00",
                "priority": 1,
                "category": "test",
            },
        )

        assert item.text == "test"
        assert item.completed
        assert item.created_at.isoformat() == "2023-01-01T00:00:00"
        assert item.completed_at
        assert item.completed_at.isoformat() == "2023-01-01T00:00:00"
        assert "Loaded item from dict" in caplog.text


class TestTodoListModel:
    """Test TodoListModel."""

    @pytest.mark.parametrize(
        ("text", "priority", "category"),
        [
            ("测试1", 0, ""),
            ("测试2", 1, "工作"),
            ("测试3", 2, "工作"),
            ("测试4", 3, "工作"),
        ],
    )
    def test_normal_functions(
        self,
        text: str,
        *,
        priority: int,
        category: str,
    ) -> None:
        """Test add item."""
        model = TodoListModel()

        # Test init state
        assert len(model.items) == 0
        assert model.count == 0

        # Test add item
        model.add_item(text, priority, category)
        assert len(model.items) == 1
        assert model.count == 1
        assert str(model.get_item(0)) == str(
            TodoItem(
                text=text,
                completed=False,
                priority=priority,
                category=category,
            ),
        )

        # Test update item
        assert model.completed_count == 0
        model.update_item(0, completed=True)
        assert model.completed_count == 1

        # Test remove item
        model.remove_item(0)
        assert model.count == 0


class TestTodoListView:
    """Test TodoListView."""

    @pytest.fixture(autouse=True)
    def fixture_reset_data(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Reset data file."""
        monkeypatch.setattr(
            "pycmd2.office.todo.controller.TodoController.get_data_file_path",
            lambda _: str(tmp_path / "todo_data.json"),
        )

    @pytest.fixture
    def mock_controller(
        self,
        qtbot: QtBot,
    ) -> Generator[TodoController, None, None]:
        """Setup controller.

        Yields:
            TodoController: TodoController instance
        """
        controller = TodoController()
        controller.show()
        qtbot.addWidget(controller.view)
        yield controller
        controller.save_data()

    def _click_item(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
        item: TodoItem,
        *,
        condition: bool = True,
    ) -> None:
        """Click item."""
        if condition:
            filtered_index = mock_controller.model.filtered_items.index(item)
            index = mock_controller.model.index(filtered_index, 0)
            qtbot.mouseClick(
                mock_controller.view.todo_list.viewport(),
                Qt.LeftButton,
                pos=mock_controller.view.todo_list.visualRect(index).center(),
            )

    def _complete_count(self, mock_controller: TodoController) -> int:
        """Get complete count.

        Returns:
            int: complete count
        """
        return sum(1 for item in mock_controller.model.items if item.completed)

    def test_add_item(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
    ) -> None:
        """Test app run."""
        assert mock_controller.view.isVisible()

        # actions
        mock_controller.view.todo_input.setText("测试待办事项")
        qtbot.mouseClick(mock_controller.view.add_button, Qt.LeftButton)

        assert mock_controller.model.count == 1
        assert isinstance(mock_controller.model.get_item(0), TodoItem)
        assert not mock_controller.model.get_item(0).completed  # pyright: ignore[reportOptionalMemberAccess]
        assert mock_controller.model.get_item(0).text == "测试待办事项"  # pyright: ignore[reportOptionalMemberAccess]

    def test_item_clicked(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test item click to toggle completion status."""
        # Add two items to the model
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        mock_controller.model.add_item("Test todo item 02", 2, "work")

        assert mock_controller.model.count == 2  # noqa: PLR2004
        assert mock_controller.model.get_item(0).completed is False  # pyright: ignore[reportOptionalMemberAccess]
        assert mock_controller.model.get_item(1).completed is False  # pyright: ignore[reportOptionalMemberAccess]

        mock_controller.model.add_item("Test todo item 03", 3, "play")
        assert mock_controller.model.count == 3  # noqa: PLR2004
        assert mock_controller.model.get_item(2).completed is False  # pyright: ignore[reportOptionalMemberAccess]

        # Click first item to complete it
        first_item = mock_controller.model.get_item(0)
        assert first_item is not None
        self._click_item(
            mock_controller,
            qtbot,
            first_item,
            condition=not first_item.completed,
        )
        assert self._complete_count(mock_controller) == 1

        # Click other items to complete it
        for _, item in enumerate(mock_controller.model.items):
            self._click_item(
                mock_controller,
                qtbot,
                item,
                condition=not item.completed,
            )

        # Check that one item is now completed
        assert self._complete_count(mock_controller) == 3  # noqa: PLR2004

        # Mock the confirmation dialog for un-completing
        monkeypatch.setattr(
            QMessageBox,
            "exec_",
            lambda _: QMessageBox.StandardButton.Yes,  # type: ignore
        )

        # Find the completed item and click it to un-complete
        for _, item in enumerate(mock_controller.model.items):
            self._click_item(
                mock_controller,
                qtbot,
                item,
                condition=item.completed,
            )
        assert self._complete_count(mock_controller) == 0

    def test_item_right_clicked(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
    ) -> None:
        """Test app close."""
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        index = mock_controller.model.index(0, 0)
        qtbot.mouseClick(
            mock_controller.view.todo_list.viewport(),
            Qt.RightButton,
            pos=mock_controller.view.todo_list.visualRect(index).center(),
        )

    def test_context_menu_event_edit(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu edit action."""
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Mock the QInputDialog to return a specific text
        monkeypatch.setattr(
            "PyQt5.QtWidgets.QInputDialog.getText",
            lambda _, __: ("Updated item text", True),
        )

        # Get the position of the item
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)

        # Simulate right-click to open context menu
        qtbot.mouseClick(
            mock_controller.view.todo_list.viewport(),
            Qt.RightButton,
            pos=rect.center(),
        )

        # Note: We cannot interact with the context menu via key events
        # because it's a separate popup menu, not part of the list widget.
        # The proper way to test context menu functionality is through
        # direct method calls, as implemented in the direct_call tests.

    def test_context_menu_event_delete(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu delete action."""
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Mock the confirmation dialog to automatically confirm deletion
        monkeypatch.setattr(
            "PyQt5.QtWidgets.QMessageBox.exec_",
            lambda _: QMessageBox.StandardButton.Yes,  # pyright: ignore[reportAttributeAccessIssue]
        )

        # Get the position of the item
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)

        # Simulate right-click to open context menu
        qtbot.mouseClick(
            mock_controller.view.todo_list.viewport(),
            Qt.RightButton,
            pos=rect.center(),
        )

        # Note: We cannot interact with the context menu via key events
        # because it's a separate popup menu, not part of the list widget.
        # The proper way to test context menu functionality is through
        # direct method calls, as implemented in the direct_call tests.

    def test_context_menu_event_set_priority(
        self,
        mock_controller: TodoController,
        qtbot: QtBot,
    ) -> None:
        """Test context menu set priority action."""
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Get the position of the item
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)

        # Simulate right-click to open context menu
        qtbot.mouseClick(
            mock_controller.view.todo_list.viewport(),
            Qt.RightButton,
            pos=rect.center(),
        )

        # Note: We cannot interact with the context menu via key events
        # because it's a separate popup menu, not part of the list widget.
        # The proper way to test context menu functionality is through
        # direct method calls, as implemented in the direct_call tests.

    def test_context_menu_event_direct_call_edit(
        self,
        mock_controller: TodoController,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu event by directly calling the method for edit action."""  # noqa: E501
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Get the item's index and position
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)
        global_pos = mock_controller.view.todo_list.mapToGlobal(rect.center())

        # Mock QInputDialog.getText to return specific values
        monkeypatch.setattr(
            "PyQt5.QtWidgets.QInputDialog.getText",
            lambda *args, **kwargs: ("Edited item text", True),  # noqa: ARG005
        )

        # Mock QMenu.exec_ to return the edit action

        def mock_exec(self: QObject, pos: QPoint) -> None:  # noqa: ARG001
            """Mock QMenu.exec_."""
            actions = self.actions()
            for action in actions:
                if action.text() == "编辑":
                    return action
            return None

        monkeypatch.setattr("PyQt5.QtWidgets.QMenu.exec_", mock_exec)

        # Create a context menu event
        event = QContextMenuEvent(
            QContextMenuEvent.Mouse,
            global_pos,
            global_pos,
        )

        # Call contextMenuEvent directly
        mock_controller.view.contextMenuEvent(event)

        # Check that the item text was updated
        assert mock_controller.model.get_item(0).text == "Edited item text"  # pyright: ignore[reportOptionalMemberAccess]

    def test_context_menu_event_direct_call_delete(
        self,
        mock_controller: TodoController,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu event by directly calling the method for delete action."""  # noqa: E501
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Get the item's index and position
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)
        global_pos = mock_controller.view.todo_list.mapToGlobal(rect.center())

        # Mock QMenu.exec_ to return the delete action
        def mock_exec(self: QObject, pos: QPoint) -> None:  # noqa: ARG001
            """Mock QMenu.exec."""
            actions = self.actions()
            for action in actions:
                if action.text() == "删除":
                    return action
            return None

        monkeypatch.setattr("PyQt5.QtWidgets.QMenu.exec_", mock_exec)

        # Create a context menu event
        event = QContextMenuEvent(
            QContextMenuEvent.Mouse,
            global_pos,
            global_pos,
        )

        # Mock the item_deleted signal
        deleted_row = []

        def capture_deleted_row(row: int) -> None:
            deleted_row.append(row)

        mock_controller.view.item_deleted.connect(capture_deleted_row)

        # Call contextMenuEvent directly
        mock_controller.view.contextMenuEvent(event)

        # Check that the delete signal was emitted with correct row
        assert deleted_row == [0]

    def test_context_menu_event_direct_call_set_priority(
        self,
        mock_controller: TodoController,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu event by directly calling the method for set priority action."""  # noqa: E501
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Get the item's index and position
        index = mock_controller.model.index(0, 0)
        rect = mock_controller.view.todo_list.visualRect(index)
        global_pos = mock_controller.view.todo_list.mapToGlobal(rect.center())

        # Mock QMenu.exec_ to return the "高" priority action
        def mock_exec(self: QObject, pos: QPoint) -> None:  # noqa: ARG001
            """Mock QMenu.exec."""
            # Find the "设置优先级" menu
            for action in self.actions():
                if action.menu():
                    # This is the priority submenu
                    priority_actions = action.menu().actions()
                    # Return the "高" priority action (index 3)
                    return priority_actions[3]
            return None

        monkeypatch.setattr("PyQt5.QtWidgets.QMenu.exec_", mock_exec)

        # Create a context menu event
        event = QContextMenuEvent(
            QContextMenuEvent.Mouse,
            global_pos,
            global_pos,
        )

        # Call contextMenuEvent directly
        mock_controller.view.contextMenuEvent(event)

        # Check that the item priority was updated to "高" (index 3)
        assert mock_controller.model.get_item(0).priority == 3  # pyright: ignore[reportOptionalMemberAccess] # noqa: PLR2004

    def test_context_menu_event_with_invalid_index(
        self,
        mock_controller: TodoController,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test context menu event when clicking on an invalid index (empty area)."""  # noqa: E501
        # Add an item to test with
        mock_controller.model.add_item("Test todo item 01", 1, "work")
        assert mock_controller.model.count == 1

        # Get a position that is not on any item (e.g., at y=1000)
        global_pos = mock_controller.view.todo_list.mapToGlobal(
            mock_controller.view.todo_list.rect().topLeft(),
        )
        # Move the point to ensure it's not over any item
        global_pos += QPoint(0, 1000)

        # Create a context menu event
        event = QContextMenuEvent(
            QContextMenuEvent.Mouse,
            global_pos,
            global_pos,
        )

        # Mock QMenu.exec_ to ensure it doesn't cause issues
        menu_executed = []

        def mock_exec(self: QObject, pos: QPoint) -> None:  # noqa: ARG001
            menu_executed.append(True)

        monkeypatch.setattr("PyQt5.QtWidgets.QMenu.exec_", mock_exec)

        # Call contextMenuEvent directly - should not raise any exception
        mock_controller.view.contextMenuEvent(event)

        # Ensure that menu.exec_ was not called since index is invalid
        assert len(menu_executed) == 0

    def test_backup_execution(
        self,
        mock_controller: TodoController,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test backup execution through timer timeout."""
        # Collect calls to subprocess.call and os.chdir
        calls = []
        chdir_calls = []

        def mock_subprocess_call(
            cmd: str,
            *_: list[str],
            **__: dict[str, str],
        ) -> int:
            calls.append(cmd)
            return 0

        def mock_chdir(path: str) -> None:
            chdir_calls.append(path)

        monkeypatch.setattr(subprocess, "call", mock_subprocess_call)
        monkeypatch.setattr(os, "chdir", mock_chdir)

        # Find the backup timer
        timers = [
            child
            for child in mock_controller.view.children()
            if child.__class__.__name__ == "QTimer"
        ]
        backup_interval = 1000 * 60 * conf.BACKUP_INTEVAL
        backup_timers = [
            timer for timer in timers if timer.interval() == backup_interval
        ]

        assert len(backup_timers) == 1
        backup_timer = backup_timers[0]

        # Trigger the timeout to execute the backup function
        backup_timer.timeout.emit()

        # Verify that the backup function was called correctly
        assert len(chdir_calls) == 1
        assert str(conf.data_dir()) in chdir_calls[0]
        assert len(calls) == 1
        assert calls[0] == ["folderb", "--max-count", "100"]
