import os
import pathlib
import sys
import typing
from dataclasses import dataclass

from PySide2.QtCore import QProcess
from PySide2.QtCore import QTextStream
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
from pycmd2.common.gui import setup_pyside2_env
from pycmd2.common.settings import get_settings

setup_pyside2_env()

cli = get_client()
settings = get_settings(
    config_name="llama_server",
    default_config=dict(model_path=""),
)


@dataclass
class Config:
    """配置数据类"""

    title: str
    size: typing.Tuple[int, int]
    listen_port_range: typing.Tuple[int, int]
    default_listen_port: int
    listen_url: str
    threads_range: typing.Tuple[int, int]
    default_threads: int


CONFIG = Config(
    title="Llama 本地模型管理器",
    size=(800, 800),
    listen_port_range=(1024, 65535),
    default_listen_port=8080,
    listen_url="http://127.0.0.1:8080",
    threads_range=(1, 24),
    default_threads=4,
)


class LlamaServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(CONFIG.title)
        self.resize(*CONFIG.size)

        self.process = None
        self.init_ui()
        self.setup_process()

        model_path = settings.get("model_path", "")
        if model_path:
            self.model_path_input.setText(str(model_path))
        else:
            self.model_path_input.setPlaceholderText("选择或输入模型文件路径")

    def init_ui(self):
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
        self.port_spin.setRange(*CONFIG.listen_port_range)
        self.port_spin.setValue(CONFIG.default_listen_port)
        params_layout.addWidget(self.port_spin)

        params_layout.addWidget(QLabel("线程数:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(*CONFIG.threads_range)
        self.threads_spin.setValue(CONFIG.default_threads)
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

    def create_text_format(self, color):
        format = QTextCharFormat()
        format.setForeground(color)
        return format

    def setup_process(self):
        """初始化进程"""

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)

    def on_load_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            settings.get("model_path", ""),
            "模型文件 (*.bin *.gguf)",
        )
        if path:
            settings.set("model_path", path)

            self.model_path_input.setText(os.path.normpath(path))

    def toggle_server(self):
        if self.process.state() == QProcess.Running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
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
        except Exception as e:
            self.append_output(f"启动失败: {str(e)}", self.error_format)

    def stop_server(self):
        if self.process.state() == QProcess.Running:
            self.append_output("正在停止服务器...", self.info_format)
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                self.process.kill()

    def on_start_browser(self):
        QDesktopServices.openUrl(CONFIG.listen_url)

    def on_process_finished(self, exit_code, exit_status):
        self.append_output(
            f"\n服务器已停止，退出码: {exit_code}，退出状态: {exit_status}\n",
            self.info_format,
        )
        self.update_ui_state(running=False)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = QTextStream(data).readAll()
        self.append_output(text, self.info_format)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = QTextStream(data).readAll()
        self.append_output(text, self.error_format)

    def append_output(
        self, text: str, text_format: typing.Optional[QTextCharFormat] = None
    ):
        cursor: QTextCursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        if text_format:
            cursor.setCharFormat(text_format)

        cursor.insertText(text)
        self.output_area.setTextCursor(cursor)
        self.output_area.ensureCursorVisible()

    def update_ui_state(self, running: bool):
        self.model_path_input.setEnabled(not running)
        self.load_model_btn.setEnabled(not running)
        self.port_spin.setEnabled(not running)
        self.threads_spin.setEnabled(not running)
        self.browser_btn.setEnabled(running)

        if running:
            self.start_btn.setText("停止服务器")
        else:
            self.start_btn.setText("启动服务器")


def main():
    app = QApplication(sys.argv)
    window = LlamaServerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
