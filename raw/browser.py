import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QFileDialog, QListWidget, QPushButton, \
    QGridLayout, QLabel, QVBoxLayout, QWidget, QDialog, QListWidgetItem
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6 import QtCore, QtGui


class MediaViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('Media Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Create the toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add the "Browse" button to the toolbar
        browse_action = QAction('Browse', self)
        browse_action.triggered.connect(self.browse_folder)
        toolbar.addAction(browse_action)

        # Add the "List view" button to the toolbar
        list_view_action = QAction('List view', self)
        list_view_action.triggered.connect(self.show_list_view)
        toolbar.addAction(list_view_action)

        # Add the "Grid view" button to the toolbar
        grid_view_action = QAction('Grid view', self)
        grid_view_action.triggered.connect(self.show_grid_view)
        toolbar.addAction(grid_view_action)

        # Set up the main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Set up the list widget
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # Set up the grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        main_layout.addLayout(self.grid_layout)

        # Set the initial view to list view
        self.list_view = True
        self.show_list_view()

    def browse_folder(self):
        # Let the user select a folder
        folder_path = QFileDialog.getExistingDirectory(self, 'Select a folder')
        if folder_path:
            # Clear the list and grid view
            self.list_widget.clear()
            for i in reversed(range(self.grid_layout.count())):
                widgetToRemove = self.grid_layout.itemAt(i).widget()
                # remove it from the layout list
                self.grid_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            # Add the media files in the selected folder to the list view and grid layout
            media_files = [f for f in os.listdir(
                folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for i, media_file in enumerate(media_files):
                # Add the media file to the list view
                item = QListWidgetItem(media_file)
                self.list_widget.addItem(item)

                # Add the media file to the grid layout
                is_image = media_file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp'))
                if is_image:
                    pixmap = QPixmap(os.path.join(folder_path, media_file))
                    pixmap_label = QLabel()
                    pixmap_label.setPixmap(pixmap.scaledToWidth(150))
                    pixmap_label.mousePressEvent = lambda event, arg1=os.path.join(
                        folder_path, media_file), arg2=True: self.show_media(arg1, arg2)
                    self.grid_layout.addWidget(pixmap_label, i // 4, i % 4)
                else:
                    button = QPushButton(media_file)
                    button.clicked.connect(lambda checked, arg1=os.path.join(
                        folder_path, media_file), arg2=False: self.show_media(arg1, arg2))
                    self.grid_layout.addWidget(button, i // 4, i % 4)

    def show_media(self, media_file, is_image):
        if is_image:
            # If it's an image, show a dialog with the image
            dialog = QDialog(self)
            dialog.setWindowTitle(media_file)
            layout = QVBoxLayout()
            dialog.setLayout(layout)
            image_label = QLabel()
            pixmap = QPixmap(media_file)
            image_label.setPixmap(pixmap.scaled(
                800, 600, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            layout.addWidget(image_label)
            dialog.exec()
        else:
            # If it's not an image, open the file with the default application
            os.startfile(media_file)

    def show_list_view(self):
        self.list_view = True
        self.list_widget.show()
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            widget.hide()

    def show_grid_view(self):
        self.list_view = False
        self.list_widget.hide()
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MediaViewer()
    window.show()
    sys.exit(app.exec())
