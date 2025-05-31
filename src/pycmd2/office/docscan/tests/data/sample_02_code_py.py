from PySide2.QtCore import QStringListModel
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QComboBox
from PySide2.QtWidgets import QListView
from PySide2.QtWidgets import QSplitter

app = QApplication()
cities = "北京 上海 广州 深圳 武汉 成都 西安 长沙".split()
model = QStringListModel([f"城市({i}):{e}" for i, e in enumerate(cities)])

splitter = QSplitter()
view1 = QListView(splitter)
view1.setModel(model)

# QComboBox 也可以作为 ListView 进行显示
view2 = QComboBox(splitter)
view2.setModel(model)

splitter.show()
app.exec_()
