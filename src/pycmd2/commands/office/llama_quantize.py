"""GGUF量化转换GUI工具, 用于将F16格式的GGUF文件转换为其他主流量化格式."""

from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from pycmd2.client import get_client

cli = get_client(enable_qt=True, enable_high_dpi=True)
logger = logging.getLogger(__name__)


def _process_gguf_stem(filename: str) -> str:
    """处理文件名, 移除可能的F16后缀.

    Returns:
        str: 处理后的文件名
    """
    if filename.upper().endswith("-F16"):
        filename = filename[:-4]  # 移除-F16后缀
    return filename


class QuantizationWorker(QThread):
    """量化执行线程Worker."""

    progress_msg_updated = pyqtSignal(str)
    progress_count_updated = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(
        self,
        input_file: pathlib.Path,
        quant_types: list[str],
    ) -> None:
        super().__init__()

        self.input_file = input_file
        self.quant_types = quant_types
        self.input_dir = input_file.parent
        self.base_name = _process_gguf_stem(input_file.stem)
        self.total_files = len(quant_types)
        self.completed_files = 0

    def run(self) -> None:
        """执行量化转换任务."""
        try:
            for quant_type in self.quant_types:
                output_file: pathlib.Path = self.input_dir / f"{self.base_name}-{quant_type}.gguf"

                self.progress_msg_updated.emit(
                    f"正在转换到 {quant_type} 格式...",
                )

                # 构建命令行参数
                os.chdir(self.input_file.parent)
                cmd = [
                    "llama-quantize",
                    str(self.input_file.name),
                    str(output_file),
                    quant_type,
                ]

                # 执行转换命令
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )

                # 实时输出进度
                for line in process.stdout:
                    self.progress_msg_updated.emit(line.strip())

                process.wait()
                self.completed_files += 1
                progress = int((self.completed_files / self.total_files) * 100)
                self.progress_count_updated.emit(progress)

                if process.returncode == 0:
                    self.progress_msg_updated.emit(
                        f"成功生成: {output_file!s}",
                    )
                else:
                    self.progress_msg_updated.emit(f"转换 {quant_type} 失败")

            self.finished.emit(success=True)
        except subprocess.CalledProcessError as e:
            self.progress_msg_updated.emit(f"发生错误: {e!s}")
            self.finished.emit(success=False)


class GGUFQuantizerGUI(QMainWindow):
    """GGUF量化转换工具GUI界面."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GGUF量化转换工具")
        self.setGeometry(100, 100, 600, 500)

        self.input_file: pathlib.Path = pathlib.Path()
        self.worker: QuantizationWorker | None = None
        self.quant_types = {
            "Q2_K": "Q2_K (极低精度, 最小尺寸)",
            "Q3_K_S": "Q3_K_S (低精度, 小尺寸)",
            "Q3_K_M": "Q3_K_M (低精度, 中等尺寸)",
            "Q3_K_L": "Q3_K_L (低精度, 大尺寸)",
            "Q4_0": "Q4_0 (基本4位)",
            "Q4_K_S": "Q4_K_S (4位, 小尺寸)",
            "Q4_K_M": "Q4_K_M (4位, 中等尺寸)",
            "Q5_0": "Q5_0 (基本5位)",
            "Q5_K_S": "Q5_K_S (5位, 小尺寸)",
            "Q5_K_M": "Q5_K_M (5位, 中等尺寸)",
            "Q6_K": "Q6_K (6位, 高质量)",
            "Q8_0": "Q8_0 (8位, 最高质量)",
        }
        self.quant_checks = {}  # 存储量化类型对应的checkbox

        self.init_ui()

    def init_ui(self) -> None:
        """初始化界面."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 文件选择部分
        file_group = QGroupBox("选择F16格式的GGUF文件")
        file_layout = QVBoxLayout()

        self.file_label = QLabel("未选择文件")
        file_btn = QPushButton("选择文件")
        file_btn.clicked.connect(self.select_file)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_btn)
        file_group.setLayout(file_layout)

        # 量化选项部分
        quant_group = QGroupBox("选择量化类型")
        quant_layout = QGridLayout()

        for i, (quant_type, label) in enumerate(self.quant_types.items()):
            check = QCheckBox(label)
            self.quant_checks[quant_type] = check
            row = i // 2
            col = i % 2
            quant_layout.addWidget(check, row, col)

        # 主流量化类型
        self.quant_checks["Q4_K_M"].setChecked(True)
        self.quant_checks["Q5_K_M"].setChecked(True)

        quant_group.setLayout(quant_layout)

        # 进度显示部分
        progress_group = QGroupBox("转换进度")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.output_text)
        progress_group.setLayout(progress_layout)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)

        btn_layout.addWidget(self.convert_btn)

        # 组装主界面
        main_layout.addWidget(file_group)
        main_layout.addWidget(quant_group)
        main_layout.addWidget(progress_group)
        main_layout.addLayout(btn_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_file(self) -> None:
        """选择文件."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择F16格式的GGUF文件",
            "",
            "GGUF Files (*.gguf)",
        )

        if file_path:
            self.input_file = pathlib.Path(file_path)
            filename = self.input_file.name
            self.file_label.setText(filename)

            # 检查文件名是否包含F16
            if "-F16" not in filename.upper():
                self.output_text.append(
                    "注意: 输入文件名不包含F16后缀,输出文件名将直接添加量化类型",
                )
                self._scroll_to_bottom()

            # 检查已存在的量化文件
            self.check_existing_quant_files()

            self.convert_btn.setEnabled(True)
            self.output_text.clear()
            self.progress_bar.setValue(0)
            self._scroll_to_bottom()

    def check_existing_quant_files(self) -> None:
        """检查当前目录下已存在的量化文件, 并更新checkbox状态."""
        if not self.input_file:
            return

        dir_path = self.input_file.parent

        for quant_type in self.quant_types:
            filename = f"{_process_gguf_stem(self.input_file.stem)}-{quant_type}.gguf"
            expected_file = dir_path / filename
            if expected_file.exists():
                self.quant_checks[quant_type].setChecked(False)
                self.quant_checks[quant_type].setEnabled(False)
                self.quant_checks[quant_type].setText(
                    f"{self.quant_types[quant_type]} (已存在)",
                )
            else:
                self.quant_checks[quant_type].setEnabled(True)
                self.quant_checks[quant_type].setText(
                    self.quant_types[quant_type],
                )
                self.quant_checks[quant_type].setStyleSheet("")

    def _scroll_to_bottom(self) -> None:
        """滚动输出框到底部."""
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_conversion(self) -> None:
        """开始转换."""
        selected_quants: list[str] = [q for q, check in self.quant_checks.items() if check.isChecked()]

        if not selected_quants:
            self.output_text.append("请至少选择一种量化类型")
            self._scroll_to_bottom()
            return

        if not self.input_file:
            self.output_text.append("请先选择输入文件")
            self._scroll_to_bottom()
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.output_text.append(f"开始转换: {self.input_file!s}")
        self.output_text.append(f"选择的量化类型: {', '.join(selected_quants)}")
        self.output_text.append(f"将生成 {len(selected_quants)} 个量化文件")

        self.worker = QuantizationWorker(self.input_file, selected_quants)
        self.worker.progress_msg_updated.connect(self.update_progress_msg)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.progress_count_updated.connect(self.update_progress_value)
        self.worker.start()

    @pyqtSlot(str)
    def update_progress_msg(self, message: str) -> None:
        """更新进度信息."""
        self.output_text.append(message)
        self.output_text.ensureCursorVisible()
        self._scroll_to_bottom()

    @pyqtSlot(int)
    def update_progress_value(self, value: int) -> None:
        """更新进度条."""
        self.progress_bar.setValue(value)

    @pyqtSlot(bool)
    def conversion_finished(self, *, success: bool) -> None:
        """转换完成回调函数."""
        self.convert_btn.setEnabled(True)
        if success:
            self.output_text.append("所有量化转换完成!")
            self.progress_bar.setValue(100)
        else:
            self.output_text.append("量化转换过程中出现错误!")


def main() -> None:
    app = QApplication(sys.argv)

    # 检查是否安装了llama.cpp
    try:
        subprocess.run(
            ["llama-quantize", "--help"],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        logger.exception("错误: 未找到llama.cpp/quantize工具")
        logger.exception(
            "请确保已编译llama.cpp并将quantize工具放在llama.cpp/目录下",
        )
        sys.exit(1)

    window = GGUFQuantizerGUI()
    window.show()
    sys.exit(app.exec_())
