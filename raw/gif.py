import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from PyQt6.QtGui import QMovie

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GIF Player")
        self.setGeometry(100, 100, 400, 400)

        self.label = QLabel(self)
        self.label.setGeometry(50, 50, 300, 300)

        self.movie = QMovie()
        self.label.setMovie(self.movie)

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")

        self.open_action = self.file_menu.addAction("Open")
        self.open_action.triggered.connect(self.open_file)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open GIF file", "", "GIF Files (*.gif)")
        if file_name:
            self.movie.setFileName(file_name)
            self.movie.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())