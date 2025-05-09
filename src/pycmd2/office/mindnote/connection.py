from PySide2.QtCore import Qt
from PySide2.QtGui import QPainterPath
from PySide2.QtGui import QPen
from PySide2.QtWidgets import QGraphicsPathItem


class Connection(QGraphicsPathItem):
    def __init__(self, start_node, end_node=None):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.darkGray, 2, Qt.DashLine))
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        start_pos = self.start_node.mapToScene(self.start_node.rect().center())
        if self.end_node:
            end_pos = self.end_node.mapToScene(self.end_node.rect().center())
            path.moveTo(start_pos)
            path.lineTo(end_pos)
        else:
            path.moveTo(start_pos)
            path.lineTo(self.scenePos())
        self.setPath(path)

    def delete_connection(self):
        self.start_node.connections.remove(self)
        if self.end_node:
            self.end_node.connections.remove(self)
        self.scene().removeItem(self)
