import pytest

from pycmd2.office.todo.model import TodoItem


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
