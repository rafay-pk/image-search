import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QModelIndex, Qt, QDir


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('File Explorer')

        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)
        # self.tree.setRootIndex(self.model.index(''))
        for column in range(1, self.model.columnCount()):
            self.tree.setColumnHidden(column, True)
        self.setCentralWidget(self.tree)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
