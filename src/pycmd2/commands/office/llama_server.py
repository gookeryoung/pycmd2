from __future__ import annotations

import logging
import os
import pathlib
import sys
from typing import ClassVar

from PyQt5.QtCore import QProcess
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QMoveEvent
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from pycmd2.client import get_client
from pycmd2.config import TomlConfigMixin


class LlmServerConfig(TomlConfigMixin):
    """Configuration for Llama local model server."""

    TITLE: str = "Llama local model server"
    WIN_SIZE: ClassVar[list[int]] = [800, 800]
    WIN_POS: ClassVar[list[int]] = [200, 200]
    MODEL_PATH: str = ""

    URL: str = "http://127.0.0.1"
    LISTEN_PORT: int = 8080
    LISTEN_PORT_RNG: ClassVar[list[int]] = [1024, 65535]
    THREAD_COUNT_RNG: ClassVar[list[int]] = [1, 24]
    THREAD_COUNT: int = 4


cli = get_client(enable_qt=True, enable_high_dpi=False)
conf = LlmServerConfig()
logger = logging.getLogger(__name__)


class LlamaServerGUI(QMainWindow):
    """Llama local model server GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(conf.TITLE)
        self.setGeometry(*conf.WIN_POS, *conf.WIN_SIZE)

        self.process: QProcess
        self.init_ui()
        self.setup_process()

        model_path = conf.MODEL_PATH
        if model_path:
            self.model_path_input.setText(str(model_path))
        else:
            self.model_path_input.setPlaceholderText("Choose model file...")

    def init_ui(self) -> None:
        """Initialize UI."""
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()  # type: ignore

        # Configuration panel
        config_group = QGroupBox("Server Configuration")
        config_layout = QVBoxLayout(config_group)

        # Model path selection
        model_path_layout = QHBoxLayout()  # type: ignore
        model_path_layout.addWidget(QLabel("Model Path:"))
        self.model_path_input = QLineEdit()

        model_path_layout.addWidget(self.model_path_input)
        self.load_model_btn = QPushButton("Browse...")
        self.load_model_btn.clicked.connect(self.on_load_model)  # type: ignore
        model_path_layout.addWidget(self.load_model_btn)
        config_layout.addLayout(model_path_layout)

        # Server parameters
        params_layout = QHBoxLayout()  # type: ignore
        params_layout.addStretch(1)
        params_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(*conf.LISTEN_PORT_RNG)
        self.port_spin.setValue(conf.LISTEN_PORT)
        params_layout.addWidget(self.port_spin)
        self.port_spin.valueChanged.connect(self.on_config_changed)  # type: ignore

        params_layout.addWidget(QLabel("Thread Count:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(*conf.THREAD_COUNT_RNG)
        self.threads_spin.setValue(conf.THREAD_COUNT)
        params_layout.addWidget(self.threads_spin)
        config_layout.addLayout(params_layout)
        self.threads_spin.valueChanged.connect(self.on_config_changed)  # type: ignore

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Control buttons
        control_layout = QHBoxLayout()  # type: ignore
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.toggle_server)  # type: ignore
        self.browser_btn = QPushButton("Start Browser")
        self.browser_btn.setEnabled(False)
        self.browser_btn.clicked.connect(self.on_start_browser)  # type: ignore
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.browser_btn)
        main_layout.addLayout(control_layout)

        # Output display
        output_group = QGroupBox("Server Output")
        output_layout = QVBoxLayout(output_group)
        self.output_area = QTextEdit("")
        self.output_area.setReadOnly(True)
        self.output_area.setLineWrapMode(QTextEdit.NoWrap)  # type: ignore

        # Set colors for different message types
        self.error_format = self.create_text_format(QColor(255, 0, 0))  # type: ignore
        self.warning_format = self.create_text_format(QColor(255, 165, 0))  # type: ignore
        self.info_format = self.create_text_format(QColor(0, 0, 0))  # type: ignore

        output_layout.addWidget(self.output_area)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    @staticmethod
    def create_text_format(color: QColor) -> QTextCharFormat:
        """Create text format.

        Args:
            color: Color.

        Returns:
            Text format.
        """
        text_format = QTextCharFormat()  # type: ignore
        text_format.setForeground(QBrush(color))  # type: ignore
        return text_format

    def setup_process(self) -> None:
        """Initialize process."""
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)  # type: ignore
        self.process.readyReadStandardError.connect(self.handle_stderr)  # type: ignore
        self.process.finished.connect(self.on_process_finished)  # type: ignore

    def on_config_changed(self) -> None:
        """Configuration changed."""
        conf.setattr("MODEL_PATH", self.model_path_input.text().strip())
        conf.setattr("LISTEN_PORT", self.port_spin.value())
        conf.setattr("THREAD_COUNT", self.threads_spin.value())
        conf.save()

    def on_load_model(self) -> None:
        """Select model file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model File",
            conf.MODEL_PATH,
            "Model Files (*.bin *.gguf)",
        )

        if path:
            conf.setattr("MODEL_PATH", path)
            self.model_path_input.setText(os.path.normpath(path))

    def toggle_server(self) -> None:
        """Start or stop server."""
        if self.process.state() == QProcess.Running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self) -> None:
        """Start server."""
        model_path = pathlib.Path(self.model_path_input.text().strip())
        if not model_path.exists():
            self.append_output(
                "Error: Invalid model file path",
                self.error_format,
            )
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

        self.append_output(f"Start: {' '.join(cmd)}\n", self.info_format)

        try:
            self.process.start(cmd[0], cmd[1:])
            self.update_ui_state(running=True)
        except QProcess.ProcessError as e:  # type: ignore
            self.append_output(f"Stop failed: {e!s}", self.error_format)

    def stop_server(self) -> None:
        """Stop server."""
        if self.process.state() == QProcess.Running:
            self.append_output("Stopping server...", self.info_format)
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                self.process.kill()

    @staticmethod
    def on_start_browser() -> None:
        """Start browser."""
        QDesktopServices.openUrl(QUrl(f"{conf.URL}:{conf.LISTEN_PORT}"))

    def on_process_finished(self, exit_code: int, exit_status: int) -> None:
        """Process finished."""
        self.append_output(
            f"\nServer stopped, Exit code: {exit_code}, Status: {exit_status}\n",
            self.info_format,
        )
        self.update_ui_state(running=False)

    def handle_stdout(self) -> None:
        """Handle standard output."""
        data = self.process.readAllStandardOutput()
        text = QTextStream(data).readAll()  # type: ignore
        self.append_output(text, self.info_format)

    def handle_stderr(self) -> None:
        """Handle standard error."""
        data = self.process.readAllStandardError()
        text = QTextStream(data).readAll()  # type: ignore
        self.append_output(text, self.error_format)

    def append_output(
        self,
        text: str,
        text_format: QTextCharFormat | None = None,
    ) -> None:
        """Append output."""
        cursor: QTextCursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)  # type: ignore

        if text_format:
            cursor.setCharFormat(text_format)

        cursor.insertText(text)  # type: ignore

        self.output_area.setTextCursor(cursor)
        self.output_area.ensureCursorVisible()

    def update_ui_state(self, *, running: bool) -> None:
        """Update UI state."""
        self.model_path_input.setEnabled(not running)
        self.load_model_btn.setEnabled(not running)
        self.port_spin.setEnabled(not running)
        self.threads_spin.setEnabled(not running)
        self.browser_btn.setEnabled(running)

        if running:
            self.start_btn.setText("Stop Server")
        else:
            self.start_btn.setText("Start Server")

    def moveEvent(self, event: QMoveEvent) -> None:
        """处理窗口移动事件."""
        win_pos = [self.geometry().topLeft().x(), self.geometry().topLeft().y()]
        logger.info(f"窗口移动: {win_pos}")
        conf.setattr("WIN_POS", win_pos)
        return super().moveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """处理窗口大小改变事件."""
        win_size = [self.geometry().width(), self.geometry().height()]
        logger.info(f"窗口大小: {win_size}")
        conf.setattr("WIN_SIZE", win_size)
        return super().resizeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 12))  # type: ignore
    window = LlamaServerGUI()
    window.show()
    sys.exit(app.exec_())
