import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Browser")
        self.setGeometry(100, 100, 500, 500)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
        self.browse_file()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.gif *.webp)")
        if file_path:
            if file_path.endswith(".gif") or file_path.endswith(".webp"):
                movie = QMovie(file_path)
                self.label.setMovie(movie)
                movie.start()
            else:
                pixmap = QPixmap(file_path)
                self.label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
