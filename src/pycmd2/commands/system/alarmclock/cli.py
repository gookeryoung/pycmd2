from __future__ import annotations

import logging
import random
import sys
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import partial
from typing import ClassVar

import qdarkstyle
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTimeEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin

__version__ = "0.1.2"
__build_date__ = "2025-09-16"


class AlarmClockConfig(TomlConfigMixin):
    """闹钟配置项."""

    ALARM_CLOCK_TITLE = "数字闹钟"

    DIGITAL_FONT: str = "bold italic 81px 'Consolas'"
    DIGITAL_COLOR: str = "#ccee00"
    DIGITAL_BORDER_COLORS: ClassVar[list[str]] = [
        "#00aa00",
        "#eecc00",
        "#aa00aa",
        "#c0e0b0",
    ]
    DIGITAL_TIMER_FORMAT: str = "%H:%M:%S"
    DIGITAL_UPDATE_INTERVAL: int = 1000

    BLINK_TITLE: str = "闹钟提醒!"
    BLINK_CONTENT: str = "⏰ 时间到了!"
    BLINK_TYPE: str = "color"  # 可选 'color' 或 'opacity'
    BLINK_BG_COLORS: ClassVar[list[str]] = [
        "#baf1ba",
        "#f8ccc3",
        "#aab4f0",
        "#efaec0",
    ]
    BLINK_INTERVAL: ClassVar[int] = 300  # ms

    DELAY_STEPS: ClassVar[list[int]] = [1, 5, 10, 15, 30, 60]  # 分钟


cli = get_client(enable_qt=True, enable_high_dpi=True)
conf = AlarmClockConfig()
logger = logging.getLogger(__name__)


class DigitalClock(QLabel):
    """炫酷的数字时钟显示."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)  # type: ignore

        self._color = conf.DIGITAL_BORDER_COLORS[0]

        # 定时器更新当前时间
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_time)  # type: ignore
        self._timer.start(conf.DIGITAL_UPDATE_INTERVAL)  # 每秒更新一次

        self.update_time()

    def update_time(self) -> None:
        """更新当前时间显示."""
        current = datetime.now(timezone.utc) + timedelta(hours=8)  # 北京时间
        self.setText(current.strftime(conf.DIGITAL_TIMER_FORMAT))
        logger.info(f"更新时间: {current}")

        # 添加闪烁效果
        self._color = random.choice(
            [_ for _ in conf.DIGITAL_BORDER_COLORS if _ != self._color],
        )
        self.setStyleSheet(f"""
            font: {conf.DIGITAL_FONT};
            color: {conf.DIGITAL_COLOR};
            background-color: black;
            border: 2px dashed {self._color};
            border-radius: 10px;
            padding: 10px;
        """)


class BlinkDialog(QDialog):
    """闹钟提醒对话框."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(conf.BLINK_TITLE)
        self.setModal(True)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowType.Dialog,  # type: ignore
        )
        self.setFixedSize(QSize(400, 240))

        layout = QVBoxLayout()
        msg_label = QLabel(conf.BLINK_CONTENT)
        msg_label.setStyleSheet("""
            color: red;
            font-size: 24px;
        """)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore

        close_button = QPushButton("关闭闹钟")
        close_button.clicked.connect(self.accept)  # type: ignore

        layout.addWidget(msg_label)
        layout.addWidget(close_button)
        self.setLayout(layout)

        # 阻止用户通过其他方式关闭对话框, 确保只能点击按钮
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)  # type: ignore  # noqa: FBT003

        # 闪烁控制变量和定时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.update_blink)  # type: ignore
        self.blink_state = False
        self.blink_type = conf.BLINK_TYPE

        # 初始化样式
        self.bg_color = random.choice(conf.BLINK_BG_COLORS)
        self.origin_style = self.styleSheet()
        self.blink_timer.start(conf.BLINK_INTERVAL)

    def update_blink(self) -> None:
        """定时器超时, 更新闪烁状态."""
        if self.blink_type == "color":
            # 颜色闪烁逻辑
            colors = [_ for _ in conf.BLINK_BG_COLORS[:] if _ != self.bg_color]
            self.setStyleSheet(f"background-color: {random.choice(colors)}")
        elif self.blink_type == "opacity":
            # 透明度闪烁逻辑 - 注意: 某些系统可能不完全支持窗口透明度
            new_opacity = 0.3 if self.blink_state else 1.0
            self.setWindowOpacity(new_opacity)

        self.blink_state = not self.blink_state  # 切换状态

    def stop_blinking(self) -> None:
        """停止闪烁, 恢复原有样式."""
        self.blink_timer.stop()
        self.setStyleSheet(self.origin_style)  # 恢复原有样式
        self.setWindowOpacity(1.0)  # 确保透明度恢复

    def closeEvent(self, event: QCloseEvent) -> None:
        """重写关闭事件, 确保定时器停止."""
        self.stop_blinking()
        super().closeEvent(event)


class AlarmClock(QMainWindow):
    """Alarm clock GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{conf.ALARM_CLOCK_TITLE} v{__version__}")
        self.setGeometry(
            QApplication.desktop().screenGeometry().center().x() - self.width() // 4,
            QApplication.desktop().screenGeometry().center().y() - self.height() // 2,
            self.width(),
            self.height(),
        )
        self.adjustSize()

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #5a5a5a;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #6a6a6a;
            }
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QTimeEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #5a5a5a;
                padding: 5px;
                font-size: 14px;
            }
        """)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # 炫酷数字时钟显示
        self.digital_clock = DigitalClock(parent=self)
        main_layout.addWidget(self.digital_clock)

        # 闹钟时间设置
        time_layout = QHBoxLayout()
        time_label = QLabel("闹钟时间:")
        time_label.setStyleSheet("color: white; font-size: 16px;")
        self.alarm_time_edit = QTimeEdit()
        self.alarm_time_edit.setDisplayFormat("HH:mm:ss")
        self.alarm_time_edit.setTime(
            QTime.currentTime().addSecs(conf.DELAY_STEPS[0] * 60),
        )

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.alarm_time_edit)
        main_layout.addLayout(time_layout)

        delay_layout = QHBoxLayout()
        delay_label = QLabel("延时(分钟):")
        delay_label.setStyleSheet("color: white; font-size: 16px;")
        delay_layout.addWidget(delay_label)
        for minutes in conf.DELAY_STEPS:
            button = QPushButton(str(minutes))
            button.setStyleSheet("color: white; font-size: 16px;")
            button.clicked.connect(partial(self.set_delay, minutes))  # type: ignore
            delay_layout.addWidget(button)
        main_layout.addLayout(delay_layout)

        # 重复选项
        self.repeat_checkbox = QCheckBox("重复")
        main_layout.addWidget(self.repeat_checkbox)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.set_alarm_button = QPushButton("设置闹钟")
        self.set_alarm_button.clicked.connect(self.set_alarm)  # type: ignore
        self.cancel_alarm_button = QPushButton("取消闹钟")
        self.cancel_alarm_button.clicked.connect(self.cancel_alarm)  # type: ignore
        self.cancel_alarm_button.setEnabled(False)
        button_layout.addWidget(self.set_alarm_button)
        button_layout.addWidget(self.cancel_alarm_button)
        main_layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("闹钟未设置")
        self.status_label.setAlignment(Qt.AlignCenter)  # type: ignore
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 16px;")
        main_layout.addWidget(self.status_label)

        # 闹钟定时器
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarm)  # type: ignore

        # 闹钟状态
        self.alarm_set = False
        self.alarm_time: QTime = QTime()  # 明确类型

    def set_delay(self, minutes: int) -> None:
        """设置延时闹钟."""
        self.alarm_time_edit.setTime(
            QTime.currentTime().addSecs(minutes * 60),
        )

    def set_alarm(self) -> None:
        """设置闹钟."""
        self.alarm_time = self.alarm_time_edit.time()
        self.alarm_set = True
        self.alarm_timer.start(1000)  # 每秒检查一次
        self.set_alarm_button.setEnabled(False)
        self.cancel_alarm_button.setEnabled(True)
        self.status_label.setText(
            f"闹钟已设置: {self.alarm_time.toString('HH:mm:ss')}",
        )
        self.status_label.setStyleSheet(
            "color: #00ff00; font-size: 16px; font-weight: bold;",
        )

    def cancel_alarm(self) -> None:
        """取消闹钟."""
        self.alarm_set = False
        self.alarm_timer.stop()
        self.set_alarm_button.setEnabled(True)
        self.cancel_alarm_button.setEnabled(False)
        self.status_label.setText("闹钟已取消")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 16px;")

    def check_alarm(self) -> None:
        """检查是否到达闹钟时间."""
        if not self.alarm_set:
            return

        current_time = QTime.currentTime()
        if (
            current_time.hour() == self.alarm_time.hour()
            and current_time.minute() == self.alarm_time.minute()
            and current_time.second() == self.alarm_time.second()
        ):
            # 显示提醒消息
            dialog = BlinkDialog()
            dialog.exec_()

            self.status_label.setText("⏰ 闹钟响了!⏰")
            self.status_label.setStyleSheet(
                "color: #ff5555; font-size: 18px; font-weight: bold;",
            )

            # 添加闪烁效果
            self.status_label.setStyleSheet("""
                color: #ff0000;
                font-size: 18px;
                font-weight: bold;
                background-color: #330000;
                border-radius: 5px;
                padding: 5px;
            """)

            # 如果不重复则取消闹钟
            if not self.repeat_checkbox.isChecked():
                self.cancel_alarm()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    window = AlarmClock()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
