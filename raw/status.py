from PyQt6.QtCore import Qt
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QStatusBar, QSpacerItem, QSizePolicy, QWidget, QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Status Bar Example")
        self.setGeometry(100, 100, 500, 300)

        # Add status bar to the main window
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        # Add labels to status bar
        self.status_left = QLabel("Left label", self)
        self.status.addWidget(self.status_left)

        # Add spacer to push separator to the right
        spacer = QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_widget = QWidget(self)
        spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        spacer_widget.setLayout(QHBoxLayout())
        spacer_widget.layout().addItem(spacer)
        self.status.addPermanentWidget(spacer_widget)

        # Add new labels to the right side
        self.status_right_1 = QLabel("Right label 1", self)
        self.status.addPermanentWidget(self.status_right_1)

        self.status_right_2 = QLabel("Right label 2", self)
        self.status.addPermanentWidget(self.status_right_2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
