import sys, os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import *
from PyQt6.QtMultimediaWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Media Viewer")
        self.setMinimumSize(800, 600)

        # Create the widgets
        self.folder_button = QPushButton("Open Folder")
        self.list_view = QListWidget()
        self.image_label = QLabel()
        self.video_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.viewer_widget = QStackedWidget()

        # Create the docks
        self.list_dock = QDockWidget("Media List")
        self.viewer_dock = QDockWidget("Media Viewer")
        self.list_dock.setWidget(self.list_view)
        self.viewer_dock.setWidget(self.viewer_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.list_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.viewer_dock)

        # Set up the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.addWidget(self.folder_button)
        layout.addWidget(self.image_label)
        layout.addWidget(self.video_widget)

        # Connect the signals and slots
        self.folder_button.clicked.connect(self.open_folder)
        self.list_view.itemSelectionChanged.connect(self.update_viewer)

    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.homePath())
        files = [os.path.join(root, f) for root, dir, file in os.walk(path) for f in file]
        self.list_view.addItems(files)


    def update_viewer(self):
        if selected.indexes():
            file_path = selected.indexes()[0].data()
            if file_path.endswith((".jpg", ".png", ".bmp")):
                self.viewer_widget.setCurrentWidget(self.image_label)
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
            elif file_path.endswith((".mp4", ".avi", ".mkv")):
                self.viewer_widget.setCurrentWidget(self.video_widget)
                self.video_player.setSource(QUrl.fromLocalFile(file_path))
                self.video_player.setVideoOutput(self.video_widget)
                self.video_player.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
