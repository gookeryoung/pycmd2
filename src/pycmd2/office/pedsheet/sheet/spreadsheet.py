from PySide2.QtWidgets import QTableWidget
from PySide2.QtWidgets import QTableWidgetSelectionRange


class SpreadSheet(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    # def copy(self):
    #     selected = self.selected_range()
    #     content = ""
    #     for i in range(selected.rowCount()):
    #         if i > 0:
    #             content += '\n'
    #         for j in range(selected.columnCount()):
    #             if j > 0:
    #                 content += '\t'
    #             content += fo
    #
    # def formula(self, row: int, column: int):
    #     cell = Cell(row, column)

    def selected_range(self):
        ranges = self.selectedRanges()
        if ranges.isEmpty():
            return QTableWidgetSelectionRange()
        else:
            return ranges.first()
