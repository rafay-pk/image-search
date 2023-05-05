import sys
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QLabel, QSizePolicy, QMainWindow, QHBoxLayout, QSpacerItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

class ImageGridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.grid_container = QWidget(self)
        self.grid = QGridLayout(self.grid_container)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.grid_container)

        # Create layout to hold scroll area and spacer item to keep scroll bar on the right
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area)

        self.setLayout(self.main_layout)
        self.images = []

    def add_image(self, filepath):
        label = QLabel(self)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(filepath)
        scaled_pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        self.grid.addWidget(label, len(self.images) // self.columnCount, len(self.images) % self.columnCount)
        self.images.append(label)

    def clear_images(self):
        for image in self.images:
            self.grid.removeWidget(image)
            image.deleteLater()
        self.images = []

    def set_column_count(self, count):
        self.columnCount = count

    def refresh_view(self):
        self.grid.update()
        self.updateGeometry()

    def set_thumbnail_height(self, height):
        self.thumbnail_height = height
        for image in self.images:
            pixmap = image.pixmap()
            scaled_pixmap = pixmap.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
            image.setPixmap(scaled_pixmap)

    def zoom_in(self):
        self.set_thumbnail_height(self.thumbnail_height * 1.2)

    def zoom_out(self):
        self.set_thumbnail_height(self.thumbnail_height / 1.2)


# Example driver code:
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ImageGridWidget()
    widget.set_column_count(2)
    widget.set_thumbnail_height(200)
    for i in range(5):
        widget.add_image(r'C:\Users\Rafay\OneDrive\Pictures\test.jpg')
    widget.show()
    sys.exit(app.exec())
