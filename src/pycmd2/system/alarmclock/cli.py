import sys

from PySide2.QtCore import Qt
from PySide2.QtCore import QTime
from PySide2.QtCore import QTimer
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QCheckBox
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QTimeEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget


class DigitalClock(QLabel):
    """炫酷的数字时钟显示."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        # 设置字体和样式
        font = QFont("Arial", 36, QFont.Bold)  # type: ignore # noqa: PGH003
        self.setFont(font)

        # 设置文本颜色和对齐方式
        self.setStyleSheet("""
            color: #00ff00;
            background-color: black;
            border: 2px solid #00aa00;
            border-radius: 10px;
            padding: 10px;
        """)
        # 使用 int() 转换来避免类型检查错误
        self.setAlignment(Qt.AlignCenter)  # type: ignore # noqa: PGH003
        # 设置最小尺寸
        self.setMinimumHeight(100)


class AlarmClock(QMainWindow):
    """Alarm clock GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("炫酷数字闹钟")
        self.setGeometry(100, 100, 400, 300)

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
        self.digital_clock = DigitalClock()
        main_layout.addWidget(self.digital_clock)

        # 闹钟时间设置
        time_layout = QHBoxLayout()
        time_label = QLabel("闹钟时间:")
        time_label.setStyleSheet("color: white; font-size: 16px;")
        self.alarm_time_edit = QTimeEdit()
        self.alarm_time_edit.setDisplayFormat("HH:mm:ss")
        self.alarm_time_edit.setTime(
            QTime.currentTime().addSecs(60),
        )  # 默认设置为1分钟后
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.alarm_time_edit)
        main_layout.addLayout(time_layout)

        # 重复选项
        self.repeat_checkbox = QCheckBox("重复")
        main_layout.addWidget(self.repeat_checkbox)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.set_alarm_button = QPushButton("设置闹钟")
        self.set_alarm_button.clicked.connect(self.set_alarm)  # type: ignore # noqa: PGH003
        self.cancel_alarm_button = QPushButton("取消闹钟")
        self.cancel_alarm_button.clicked.connect(self.cancel_alarm)  # type: ignore # noqa: PGH003
        self.cancel_alarm_button.setEnabled(False)
        button_layout.addWidget(self.set_alarm_button)
        button_layout.addWidget(self.cancel_alarm_button)
        main_layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("闹钟未设置")
        self.status_label.setAlignment(Qt.AlignCenter)  # type: ignore # noqa: PGH003
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 16px;")
        main_layout.addWidget(self.status_label)

        # 定时器更新当前时间
        self.current_time_timer = QTimer()
        self.current_time_timer.timeout.connect(self.update_current_time)  # type: ignore # noqa: PGH003
        self.current_time_timer.start(1000)  # 每秒更新一次

        # 闹钟定时器
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarm)  # type: ignore # noqa: PGH003

        # 更新当前时间显示
        self.update_current_time()

        # 闹钟状态
        self.alarm_set = False
        self.alarm_time: QTime = QTime()  # 明确类型

    def update_current_time(self) -> None:
        """更新当前时间显示."""
        current_time = QTime.currentTime()
        time_str = current_time.toString("HH:mm:ss")
        self.digital_clock.setText(time_str)

        # 添加闪烁效果
        if current_time.second() % 2 == 0:
            self.digital_clock.setStyleSheet("""
                color: #00ff00;
                background-color: black;
                border: 2px solid #00aa00;
                border-radius: 10px;
                padding: 10px;
            """)
        else:
            self.digital_clock.setStyleSheet("""
                color: #00cc00;
                background-color: black;
                border: 2px solid #008800;
                border-radius: 10px;
                padding: 10px;
            """)

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
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # type: ignore  # noqa: PGH003

    app = QApplication(sys.argv)
    window = AlarmClock()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
