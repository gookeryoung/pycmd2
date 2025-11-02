import time

import pytest

from pycmd2.tracker import timer


class TestTracker:
    """测试计时器功能."""

    @pytest.mark.parametrize(
        ("t", "expected"),
        [(0.1, 0.1), (0.2, 0.2), (0.3, 0.3)],
    )
    def test_timer(
        self,
        t: float,
        expected: float,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试计时器功能."""

        @timer
        def func(t: float) -> None:
            time.sleep(t)

        func(t)

        assert f"函数 `func` 用时 {expected:.1f}" in caplog.text
