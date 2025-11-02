from pathlib import Path
from typing import Generator

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot

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
