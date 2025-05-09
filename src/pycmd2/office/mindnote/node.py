from PySide2.QtCore import QPointF
from PySide2.QtCore import Qt
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen
from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtWidgets import QGraphicsRectItem
from PySide2.QtWidgets import QGraphicsTextItem
from PySide2.QtWidgets import QMenu


class MindNode(QGraphicsRectItem):
    def __init__(self, text="新节点"):
        super().__init__(-50, -25, 100, 50)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        # 样式设置
        self.setBrush(QBrush(QColor("#e8f5e9")))
        self.setPen(QPen(Qt.darkGreen, 2))

        # 文本项
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setTextWidth(90)
        self.text_item.setPos(-45, -20)

        # 连接列表
        self.connections = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            view = self.scene().views()[0]
            main_window = view.parent()

            if main_window.connect_action.isChecked():
                main_window.start_connection(self)
            else:
                super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        add_child_action = menu.addAction("添加子节点")
        delete_action = menu.addAction("删除节点")
        action = menu.exec_(event.screenPos())

        if action == add_child_action:
            self.add_child_node()
        elif action == delete_action:
            self.delete_node()

    def add_child_node(self):
        child = MindNode("子节点")
        child.setPos(self.pos() + QPointF(150, 0))
        self.scene().addItem(child)

    def delete_node(self):
        for conn in self.connections:
            conn.delete_connection()
        self.scene().removeItem(self)
