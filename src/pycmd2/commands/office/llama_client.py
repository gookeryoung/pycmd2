import json
import sys

import requests
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDoubleSpinBox
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

cli = get_client(enable_qt=True, enable_high_dpi=True)


class LlamaWorker(QThread):
    """工作线程, 用于与llama-server通信."""

    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    is_finished = pyqtSignal()

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        prompt: str,
        server_url: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
    ) -> None:
        super().__init__()
        self.prompt = prompt
        self.server_url = server_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self._is_running = True

    def run(self) -> None:
        """运行线程."""
        try:  # noqa: PLR1702
            headers = {"Content-Type": "application/json"}
            data = {
                "prompt": self.prompt,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "stream": True,
            }

            with requests.post(
                f"{self.server_url}/completion",
                headers=headers,
                json=data,
                stream=True,
            ) as response:
                if response.status_code != requests.codes.ok:
                    self.error_occurred.emit(
                        f"Error: {response.status_code} - {response.text}",
                    )
                    return

                buffer = ""
                for line in response.iter_lines():
                    if not self._is_running:
                        break

                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            try:
                                json_data = json.loads(decoded_line[6:])
                                content = json_data.get("content", "")
                                buffer += content
                                self.response_received.emit(buffer)
                            except json.JSONDecodeError:
                                continue

        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Connection error: {e!s}")
        finally:
            self.is_finished.emit()

    def stop(self) -> None:
        """停止工作线程."""
        self._is_running = False


class LlamaChatApp(QMainWindow):
    """llama-chat客户端."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Llama Local Model Tool")
        self.setGeometry(100, 100, 800, 600)

        # 初始化UI
        self.init_ui()

        # 工作线程
        self.worker_thread = None

    def init_ui(self) -> None:
        """初始化UI."""
        # 主窗口布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 服务器设置组
        server_group = QGroupBox("服务器设置")
        server_layout = QHBoxLayout()

        self.server_url_input = QLineEdit("http://localhost:8080")
        self.server_url_input.setPlaceholderText("输入llama-server地址")

        self.test_connection_btn = QPushButton("测试连接")
        self.test_connection_btn.clicked.connect(self.test_connection)

        server_layout.addWidget(QLabel("服务器地址:"))
        server_layout.addWidget(self.server_url_input)
        server_layout.addWidget(self.test_connection_btn)
        server_group.setLayout(server_layout)

        # 模型参数组
        params_group = QGroupBox("模型参数")
        params_layout = QHBoxLayout()

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 4096)
        self.max_tokens_spin.setValue(256)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)

        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setValue(0.9)

        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 100)
        self.top_k_spin.setValue(40)

        params_layout.addWidget(QLabel("最大Token数:"))
        params_layout.addWidget(self.max_tokens_spin)
        params_layout.addWidget(QLabel("温度:"))
        params_layout.addWidget(self.temperature_spin)
        params_layout.addWidget(QLabel("Top P:"))
        params_layout.addWidget(self.top_p_spin)
        params_layout.addWidget(QLabel("Top K:"))
        params_layout.addWidget(self.top_k_spin)
        params_group.setLayout(params_layout)

        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("font-family: monospace;")

        # 输入区域
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("输入你的提示词...")
        self.user_input.returnPressed.connect(self.send_prompt)

        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_prompt)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.setEnabled(False)

        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.stop_btn)

        # 添加到主布局
        main_layout.addWidget(server_group)
        main_layout.addWidget(params_group)
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(input_layout)

        # 状态栏
        self.statusBar().showMessage("准备就绪")

    def test_connection(self) -> None:
        """测试与llama-server的连接."""
        server_url = self.server_url_input.text().strip()
        if not server_url:
            self.statusBar().showMessage("请输入服务器地址")
            return

        try:
            response = requests.get(f"{server_url}/health")
            if response.status_code == requests.codes.ok:
                self.statusBar().showMessage("连接成功!")
            else:
                self.statusBar().showMessage(
                    f"连接失败: {response.status_code}",
                )
        except requests.exceptions.RequestException as e:
            self.statusBar().showMessage(f"连接错误: {e!s}")

    def send_prompt(self) -> None:
        """发送提示词到llama-server."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.statusBar().showMessage("请等待当前请求完成")
            return

        prompt = self.user_input.text().strip()
        if not prompt:
            self.statusBar().showMessage("请输入提示词")
            return

        # 添加到聊天显示
        self.append_to_chat(f"You: {prompt}\nAI:", is_user=True)
        self.user_input.clear()

        # 获取参数
        server_url = self.server_url_input.text().strip()
        max_tokens = self.max_tokens_spin.value()
        temperature = self.temperature_spin.value()
        top_p = self.top_p_spin.value()
        top_k = self.top_k_spin.value()

        # 创建并启动工作线程
        self.worker_thread = LlamaWorker(
            prompt=prompt,
            server_url=server_url,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )

        # 连接信号
        self.worker_thread.response_received.connect(self.update_response)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.is_finished.connect(self.on_finished)

        # 更新UI状态
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage("正在生成响应...")

        self.worker_thread.start()

    def stop_generation(self) -> None:
        """停止生成响应."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.statusBar().showMessage("生成已停止")

    def update_response(
        self,
        text: str,
    ) -> None:
        """更新聊天显示区域."""
        # 移动光标到最后
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 检查是否已经有"AI:"前缀
        current_text = self.chat_display.toPlainText()
        if current_text.endswith("AI:"):
            # 第一次更新, 直接添加文本
            self.chat_display.insertPlainText(f" {text}")
        else:
            # 后续更新, 替换最后一行
            lines = current_text.split("\n")
            lines[-1] = f"AI: {text}"
            self.chat_display.setPlainText("\n".join(lines))

        # 滚动到底部
        self.chat_display.ensureCursorVisible()

    def append_to_chat(
        self,
        text: str,
        *,
        is_user: bool = False,
    ) -> None:
        """添加文本到聊天显示区域."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        if is_user:
            self.chat_display.setTextColor(Qt.blue)
        else:
            self.chat_display.setTextColor(Qt.black)

        self.chat_display.append(text)
        self.chat_display.setTextColor(Qt.black)  # 重置为默认颜色

    def handle_error(self, error_msg: str) -> None:
        """处理错误."""
        self.append_to_chat(f"Error: {error_msg}")
        self.statusBar().showMessage(error_msg)

    def on_finished(self) -> None:
        """线程完成时的处理."""
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("生成完成")
        self.append_to_chat("")  # 添加空行分隔对话

        # 清理线程
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None


def main() -> None:
    app = QApplication(sys.argv)

    # 设置样式
    app.setStyle("Fusion")

    window = LlamaChatApp()
    window.show()

    sys.exit(app.exec_())
