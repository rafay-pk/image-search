import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main text edit widget
        # self.setCentralWidget(QWidget())

        # Create two dockable windows
        self.dock1 = QDockWidget("Dock 1", self)
        self.dock2 = QDockWidget("Dock 2", self)

        # Add some content to the dockable windows
        self.dock1_widget = QTextEdit(self.dock1)
        self.dock1.setWidget(self.dock1_widget)
        self.dock2_widget = QTextEdit(self.dock2)
        self.dock2.setWidget(self.dock2_widget)


        # Add the dockable windows to the main window
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock2)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dock1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
