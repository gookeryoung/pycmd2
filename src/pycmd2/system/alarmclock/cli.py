import pathlib
import sys

from PySide2.QtCore import Qt
from PySide2.QtCore import QTime
from PySide2.QtCore import QTimer
from PySide2.QtCore import QUrl
from PySide2.QtMultimedia import QSoundEffect
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QCheckBox
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QTimeEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget


class AlarmClock(QMainWindow):
    """Alarm clock GUI application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("闹钟")
        self.setGeometry(100, 100, 300, 200)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 当前时间显示
        self.current_time_label = QLabel()
        self.current_time_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;",
        )
        self.current_time_label.setAlignment(Qt.AlignCenter)  # type: ignore  # noqa: PGH003
        main_layout.addWidget(self.current_time_label)

        # 闹钟时间设置
        time_layout = QHBoxLayout()
        time_label = QLabel("闹钟时间:")
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
        self.set_alarm_button.clicked.connect(self.set_alarm)  # type: ignore  # noqa: PGH003
        self.cancel_alarm_button = QPushButton("取消闹钟")
        self.cancel_alarm_button.clicked.connect(self.cancel_alarm)  # type: ignore  # noqa: PGH003
        self.cancel_alarm_button.setEnabled(False)
        button_layout.addWidget(self.set_alarm_button)
        button_layout.addWidget(self.cancel_alarm_button)
        main_layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("闹钟未设置")
        self.status_label.setAlignment(Qt.AlignCenter)  # type: ignore  # noqa: PGH003
        main_layout.addWidget(self.status_label)

        # 闹钟声音文件路径, 使用系统提示音
        self.sound_effect = QSoundEffect()
        # 使用系统默认提示音
        self.sound_effect.setSource(QUrl.fromLocalFile(self.get_system_sound()))

        # 定时器更新当前时间
        self.current_time_timer = QTimer()
        self.current_time_timer.timeout.connect(self.update_current_time)  # type: ignore  # noqa: PGH003
        self.current_time_timer.start(1000)  # 每秒更新一次

        # 闹钟定时器
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarm)  # type: ignore  # noqa: PGH003

        # 更新当前时间显示
        self.update_current_time()

        # 闹钟状态
        self.alarm_set = False
        self.alarm_time: QTime = QTime()  # 明确类型

    def get_system_sound(self) -> str:
        """Get system sound file path.

        Returns:
            str: System sound file path.
        """
        # 在Windows系统上使用默认提示音
        if sys.platform == "win32":
            # Windows系统提示音路径
            return (
                "C:/Windows/Media/Alarm01.wav"
                if pathlib.Path("C:/Windows/Media/Alarm01.wav").exists()
                else ""
            )
        # 其他系统返回空
        return ""

    def update_current_time(self) -> None:
        """更新当前时间显示."""
        current_time = QTime.currentTime()
        self.current_time_label.setText(
            f"当前时间: {current_time.toString('HH:mm:ss')}",
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

    def cancel_alarm(self) -> None:
        """取消闹钟."""
        self.alarm_set = False
        self.alarm_timer.stop()
        self.set_alarm_button.setEnabled(True)
        self.cancel_alarm_button.setEnabled(False)
        self.status_label.setText("闹钟已取消")
        # 停止播放声音
        if self.sound_effect.isPlaying():
            self.sound_effect.stop()

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
            # 播放闹钟声音
            if (
                not self.sound_effect.isPlaying()
                and self.sound_effect.source().toString()
            ):
                self.sound_effect.setLoopCount(-1)  # -1 表示无限循环播放
                self.sound_effect.play()

            # 显示提醒消息
            self.status_label.setText("闹钟响了!")

            # 如果不重复则取消闹钟
            if not self.repeat_checkbox.isChecked():
                self.cancel_alarm()


def main() -> None:
    app = QApplication(sys.argv)
    window = AlarmClock()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
