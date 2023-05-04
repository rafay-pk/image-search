import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QMovie, QResizeEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Image and Animated Image Example")
        self.setMinimumSize(400, 400)

        # Create labels to display images
        self.image_label = QLabel(self)
        self.animated_image_label = QLabel(self)

        # Load images
        self.image = QPixmap(r'C:\Users\Rafay\OneDrive\data\sample.png')
        self.animated_image = QMovie(r'C:\Users\Rafay\OneDrive\data\sample2.webp')

        # Set initial image sizes
        self.update_image_sizes()

        # Set image alignments
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.animated_image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # Add labels to the window
        self.setCentralWidget(self.image_label)
        self.statusBar().addPermanentWidget(self.animated_image_label)

        # Connect to the window's resize event to update the image sizes
        self.resizeEvent = self.update_image_sizes

        # Start the animated image
        self.animated_image.start()

    def update_image_sizes(self, event=None):
        # Update image sizes when the window is resized
        window_width = self.width()
        image_width = min(window_width, self.image.width())
        if self.image.width() > 0:
            image_height = int(image_width * self.image.height() / self.image.width())
        else:
            image_height = 0
        self.image_label.setPixmap(self.image.scaled(image_width, image_height, Qt.AspectRatioMode.KeepAspectRatio))
        self.animated_image_label.setFixedHeight(int(self.height() / 10))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
