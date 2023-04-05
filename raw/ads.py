import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout
from PyQtAds import DockAreaWidget, DockWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt ADS Example")
        self.setGeometry(100, 100, 500, 300)

        # Create dock area widget
        dock_area = DockAreaWidget(self)

        # Create dock widgets
        dock_left = DockWidget("Left Dock", dock_area)
        dock_left.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        dock_left.setWidget(QWidget(dock_left))

        dock_right = DockWidget("Right Dock", dock_area)
        dock_right.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        dock_right.setWidget(QWidget(dock_right))

        dock_bottom = DockWidget("Bottom Dock", dock_area)
        dock_bottom.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        dock_bottom.setWidget(QWidget(dock_bottom))

        # Add dock widgets to dock area widget
        dock_area.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_left)
        dock_area.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_right)
        dock_area.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock_bottom)

        # Set central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout()
        central_layout.addWidget(dock_area)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
