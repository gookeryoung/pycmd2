from __future__ import annotations

import os
import pathlib
import sys
from typing import ClassVar

from PySide2.QtCore import QProcess
from PySide2.QtCore import QTextStream
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtGui import QDesktopServices
from PySide2.QtGui import QTextCharFormat
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QFileDialog
from PySide2.QtWidgets import QGroupBox
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QSpinBox
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from pycmd2.common.cli import get_client
from pycmd2.common.config import TomlConfigMixin
from pycmd2.common.gui import setup_pyside2_env

setup_pyside2_env()


class LlmServerConfig(TomlConfigMixin):
    """配置项."""

    TITLE: str = "Llama 本地模型管理器"
    WIN_SIZE: ClassVar[list[int]] = [800, 800]
    MODEL_PATH: str = ""

    URL: str = "http://127.0.0.1"
    LISTEN_PORT: int = 8080
    LISTEN_PORT_RNG: ClassVar[list[int]] = [1024, 65535]
    THREAD_COUNT_RNG: ClassVar[list[int]] = [1, 24]
    THREAD_COUNT: int = 4


cli = get_client()
conf = LlmServerConfig()


class LlamaServerGUI(QMainWindow):
    """Llama 本地模型管理器."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(conf.TITLE)
        self.resize(*conf.WIN_SIZE)

        self.process = None
        self.init_ui()
        self.setup_process()

        model_path = conf.MODEL_PATH
        if model_path:
            self.model_path_input.setText(str(model_path))
        else:
            self.model_path_input.setPlaceholderText("选择或输入模型文件路径")

    def init_ui(self) -> None:
        """初始化界面."""
        # 主界面布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 配置面板
        config_group = QGroupBox("服务器配置")
        config_layout = QVBoxLayout()

        # 模型路径选择
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(QLabel("模型路径:"))
        self.model_path_input = QLineEdit()

        model_path_layout.addWidget(self.model_path_input)
        self.load_model_btn = QPushButton("浏览...")
        self.load_model_btn.clicked.connect(self.on_load_model)
        model_path_layout.addWidget(self.load_model_btn)
        config_layout.addLayout(model_path_layout)

        # 服务器参数
        params_layout = QHBoxLayout()
        params_layout.addStretch(1)
        params_layout.addWidget(QLabel("端口号:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(*conf.LISTEN_PORT_RNG)
        self.port_spin.setValue(conf.LISTEN_PORT)
        params_layout.addWidget(self.port_spin)

        params_layout.addWidget(QLabel("线程数:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(*conf.THREAD_COUNT_RNG)
        self.threads_spin.setValue(conf.THREAD_COUNT)
        params_layout.addWidget(self.threads_spin)
        config_layout.addLayout(params_layout)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("启动服务器")
        self.start_btn.clicked.connect(self.toggle_server)
        self.browser_btn = QPushButton("启动网页")
        self.browser_btn.setEnabled(False)
        self.browser_btn.clicked.connect(self.on_start_browser)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.browser_btn)
        main_layout.addLayout(control_layout)

        # 输出显示
        output_group = QGroupBox("服务器输出")
        output_layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setLineWrapMode(QTextEdit.NoWrap)

        # 设置不同消息类型的颜色
        self.error_format = self.create_text_format(QColor(255, 0, 0))
        self.warning_format = self.create_text_format(QColor(255, 165, 0))
        self.info_format = self.create_text_format(QColor(0, 0, 0))

        output_layout.addWidget(self.output_area)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    @staticmethod
    def create_text_format(color: QColor) -> QTextCharFormat:
        """创建文本格式.

        Args:
            color: 颜色.

        Returns:
            文本格式.
        """
        text_format = QTextCharFormat()
        text_format.setForeground(QBrush(color))
        return text_format

    def setup_process(self) -> None:
        """初始化进程."""
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)

    def on_load_model(self) -> None:
        """选择模型文件."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            conf.MODEL_PATH,
            "模型文件 (*.bin *.gguf)",
        )
        if path:
            conf.MODEL_PATH = path
            self.model_path_input.setText(os.path.normpath(path))

    def toggle_server(self) -> None:
        """启动或停止服务器."""
        if self.process.state() == QProcess.Running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self) -> None:
        """启动服务器."""
        model_path = pathlib.Path(self.model_path_input.text().strip())
        if not model_path.exists():
            self.append_output("错误: 无效的模型文件路径", self.error_format)
            return

        os.chdir(str(model_path.parent))
        cmd = [
            "llama-server",
            "--model",
            model_path.name,
            "--port",
            str(self.port_spin.value()),
            "--threads",
            str(self.threads_spin.value()),
        ]

        self.append_output(f"启动命令: {' '.join(cmd)}\n", self.info_format)

        try:
            self.process.start(cmd[0], cmd[1:])
            self.update_ui_state(running=True)
        except QProcess.ProcessError as e:
            self.append_output(f"启动失败: {e!s}", self.error_format)

    def stop_server(self) -> None:
        """停止服务器."""
        if self.process.state() == QProcess.Running:
            self.append_output("正在停止服务器...", self.info_format)
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                self.process.kill()

    @staticmethod
    def on_start_browser() -> None:
        """启动网页."""
        QDesktopServices.openUrl(f"{conf.URL}:{conf.LISTEN_PORT}")

    def on_process_finished(self, exit_code: int, exit_status: int) -> None:
        """进程结束."""
        self.append_output(
            f"\n服务器已停止, 退出码: {exit_code}, 状态: {exit_status}\n",
            self.info_format,
        )
        self.update_ui_state(running=False)

    def handle_stdout(self) -> None:
        """处理标准输出."""
        data = self.process.readAllStandardOutput()
        text = QTextStream(data).readAll()
        self.append_output(text, self.info_format)

    def handle_stderr(self) -> None:
        """处理标准错误."""
        data = self.process.readAllStandardError()
        text = QTextStream(data).readAll()
        self.append_output(text, self.error_format)

    def append_output(
        self,
        text: str,
        text_format: QTextCharFormat | None = None,
    ) -> None:
        """追加输出."""
        cursor: QTextCursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        if text_format:
            cursor.setCharFormat(text_format)

        cursor.insertText(text)
        self.output_area.setTextCursor(cursor)
        self.output_area.ensureCursorVisible()

    def update_ui_state(self, *, running: bool) -> None:
        """更新界面状态."""
        self.model_path_input.setEnabled(not running)
        self.load_model_btn.setEnabled(not running)
        self.port_spin.setEnabled(not running)
        self.threads_spin.setEnabled(not running)
        self.browser_btn.setEnabled(running)

        if running:
            self.start_btn.setText("停止服务器")
        else:
            self.start_btn.setText("启动服务器")


def main() -> None:
    app = QApplication(sys.argv)
    window = LlamaServerGUI()
    window.show()
    sys.exit(app.exec_())
