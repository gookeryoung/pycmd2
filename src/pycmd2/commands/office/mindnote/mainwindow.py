import json
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QToolBar

from .connection import Connection
from .node import MindNode


class MindMapWindow(QMainWindow):
    """主界面."""

    def __init__(self) -> None:
        super().__init__()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # 初始化属性
        self.selected_node = None
        self.dragging = False
        self.connecting = False
        self.connection_start_node = None
        self.temp_connection = None

        # 创建工具栏
        self.create_toolbar()

        # 设置场景属性
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.view.setRenderHint(QPainter.Antialiasing)

    def create_toolbar(self) -> None:
        """创建工具栏."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # 添加节点动作
        add_node_action = QAction("+ 添加节点", self)
        add_node_action.triggered.connect(self.add_root_node)
        toolbar.addAction(add_node_action)

        # 连接模式切换
        self.connect_action = QAction("🔗 连接模式", self)
        self.connect_action.setCheckable(True)
        self.connect_action.setShortcut(QKeySequence("Ctrl+L"))
        self.connect_action.toggled.connect(self.toggle_connect_mode)
        toolbar.addAction(self.connect_action)

        # 文件操作
        save_action = QAction("💾 保存", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_mindmap)
        toolbar.addAction(save_action)

        load_action = QAction("📂 打开", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_mindmap)
        toolbar.addAction(load_action)

    def add_root_node(self) -> None:
        """添加根节点."""
        node = MindNode("中心主题")
        self.scene.addItem(node)
        # 将节点放置在视图中心
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        node.setPos(view_center)

    def toggle_connect_mode(self, *, checked: bool) -> None:
        """切换连接模式."""
        self.connecting = checked
        if checked:
            self.setCursor(Qt.CrossCursor)  # 进入连接模式时显示十字光标
        else:
            self.unsetCursor()  # 退出时恢复默认光标

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理场景空白处的点击."""
        if event.button() == Qt.LeftButton and self.connect_action.isChecked():
            # 在空白处点击时开始新连接
            self.start_connection(None, event)
        else:
            super().mousePressEvent(event)

    def start_connection(self, node: MindNode) -> None:
        """开始创建连接."""
        if node is None:
            global_pos = QCursor.pos()  # 获取全局坐标
            viewport_pos = self.view.mapFromGlobal(global_pos)  # 转换为视图坐标
            scene_pos = self.view.mapToScene(viewport_pos)  # 转换为场景坐标

            # 在空白处创建新节点作为起点
            node = MindNode("新节点")
            node.setPos(scene_pos)
            self.scene.addItem(node)

        self.connection_start_node = node
        self.temp_connection = Connection(node)
        self.scene.addItem(self.temp_connection)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """处理场景内鼠标移动事件."""
        if self.temp_connection:
            self.temp_connection.update_path()

        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """处理场景内鼠标释放事件."""
        if self.temp_connection:
            items = self.scene.items(event.pos())
            for item in items:
                if isinstance(item, MindNode) and item != self.connection_start_node:
                    # 完成连接
                    self.temp_connection.end_node = item
                    self.temp_connection.update_path()
                    self.connection_start_node.connections.append(
                        self.temp_connection,
                    )
                    item.connections.append(self.temp_connection)
                    self.temp_connection = None
                    return
            # 取消未完成的连接
            self.scene.removeItem(self.temp_connection)
            self.temp_connection = None

    def save_mindmap(self) -> None:
        """保存思维导图."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存思维导图",
            "",
            "MindMap Files (*.mm)",
        )
        if not path:
            return

        data = {"nodes": [], "connections": []}

        # 收集节点数据
        nodes = [item for item in self.scene.items() if isinstance(item, MindNode)]
        for node in nodes:
            node_data = {
                "text": node.text_item.toPlainText(),
                "pos": (node.x(), node.y()),
                "connections": [],
            }
            data["nodes"].append(node_data)

        # 收集连接数据
        connections = [item for item in self.scene.items() if isinstance(item, Connection)]
        for conn in connections:
            if conn.end_node:
                start_idx = nodes.index(conn.start_node)
                end_idx = nodes.index(conn.end_node)
                data["connections"].append((start_idx, end_idx))

        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_mindmap(self) -> None:
        """加载思维导图."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开思维导图",
            "",
            "MindMap Files (*.mm)",
        )
        if not path:
            return

        with Path(path).open(encoding="utf-8") as f:
            data = json.load(f)

        self.scene.clear()

        # 重建节点
        nodes = []
        for node_data in data["nodes"]:
            node = MindNode(node_data["text"])
            node.setPos(*node_data["pos"])
            self.scene.addItem(node)
            nodes.append(node)

        # 重建连接
        for conn_data in data["connections"]:
            start_node = nodes[conn_data[0]]
            end_node = nodes[conn_data[1]]
            connection = Connection(start_node, end_node)
            self.scene.addItem(connection)
            start_node.connections.append(connection)
            end_node.connections.append(connection)
