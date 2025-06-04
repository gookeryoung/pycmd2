from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QPainterPath
from PySide2.QtGui import QPen
from PySide2.QtWidgets import QGraphicsPathItem

from .node import MindNode


class Connection(QGraphicsPathItem):
    """思维导图节点连接."""

    def __init__(
        self,
        start_node: MindNode,
        end_node: Optional[MindNode] = None,
    ) -> None:
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(Qt.darkGray, 2, Qt.DashLine))
        self.update_path()

    def update_path(self) -> None:
        """更新连接路径."""
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

    def delete_connection(self) -> None:
        """删除连接."""
        self.start_node.connections.remove(self)
        if self.end_node:
            self.end_node.connections.remove(self)
        self.scene().removeItem(self)
