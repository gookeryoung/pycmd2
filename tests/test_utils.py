import re
import time

import pytest

from pycmd2.utils import timer


class TestTracker:
    """测试计时器功能."""

    @pytest.mark.parametrize(
        ("t", "tolerance"),
        [(0.1, 0.05), (0.2, 0.05), (0.3, 0.05)],
    )
    def test_timer(
        self,
        t: float,
        tolerance: float,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试计时器功能."""

        @timer
        def func(t: float) -> None:
            time.sleep(t)

        func(t)

        # 从日志中提取实际时间值

        log_text = caplog.text
        match = re.search(r"函数 `func` 用时 ([\d.]+) s", log_text)
        assert match, f"未找到时间信息在日志中: {log_text}"

        actual_time = float(match.group(1))
        # 验证实际时间在预期范围内, 考虑系统调度误差
        assert abs(actual_time - t) <= tolerance, (
            f"实际时间 {actual_time}s 与预期 {t}s 差异超过容差 {tolerance}s"
        )
