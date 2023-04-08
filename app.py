import sys, os
from PyQt6.QtCore import Qt, QSize, QDir, QSize
from PyQt6.QtGui import QFileSystemModel, QPixmap, QMovie, QIcon,  QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QLineEdit,
    QPushButton,
    QTreeView,
    QListView,
    QDockWidget,
    QToolBar
)


class MainWindow(QMainWindow):
    def __init__(self):

        # region Setup
        super().__init__()
        self.setWindowTitle("Media Magic")
        self.resize(QSize(500, 300))
        # endregion

        # region Menu Bar
        self.menu_bar = self.menuBar()
        self.menu_file = self.menu_bar.addMenu("File")
        self.action_newView = self.menu_file.addAction("New View \tCtrl+N")
        self.action_newView.setStatusTip("Create a New View of your Media Files")
        self.action_openView = self.menu_file.addAction("Open View \tCtrl+O")
        self.action_openView.setStatusTip("Open an Existing View of your Media Files")
        self.action_duplicateView = self.menu_file.addAction("Duplicate View \tCtrl+D")
        self.action_duplicateView.setStatusTip("Duplicate this View of your Media Files")
        self.action_saveView = self.menu_file.addAction("Save View \tCtrl+S")
        self.action_saveView.setStatusTip("Save this View of your Media Files")
        self.action_saveAsView = self.menu_file.addAction("Save View As... \tCtrl+Shift+S")
        self.action_saveAsView.setStatusTip("Save As... this View of your Media Files")
        self.menu_file.addSeparator()
        self.action_importTags = self.menu_file.addAction("Import Tags from View")

        self.menu_view = self.menu_bar.addMenu("View")
        self.action_addFolder = self.menu_view.addAction("Add Folder \tCtrl+Shift+A")
        self.action_addFolder.setStatusTip("Add a Parent Directory to this View")
        self.action_addFolder.triggered.connect(self.add_folder)

        self.menu_help = self.menu_bar.addMenu("Help")
        self.action_about = self.menu_help.addAction("About Media Magic")
        self.action_about.setStatusTip("Know more about this software")
        self.action_about.triggered.connect(self.show_about)

        # DEV
        self.menu_dev = self.menu_bar.addMenu("Dev")
        self.action_openFile = self.menu_dev.addAction("Open File")
        self.action_openFile.triggered.connect(self.open_file)
        # DEV
        # endregion

        # region Search Bar
        self.search_bar = QLineEdit()
        self.search_enter = QPushButton("Search")
        self.search_enter.pressed.connect(self.search)
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.search_bar)
        searchLayout.addWidget(self.search_enter)
        searchLayout.setContentsMargins(0, 0, 0, 0)
        searchLayout.setSpacing(0)
        searchBar = QWidget()
        searchBar.setLayout(searchLayout)
        self.dock_search = QDockWidget("Search")
        self.dock_search.setWidget(searchBar)
        self.dock_search.setMaximumSize(self.maximumWidth(), 25)
        hidder = QDockWidget()
        self.dock_search.setTitleBarWidget(hidder)
        hidder.setVisible(False)
        # endregion
        
        # region Folder View
        self.folders = QTreeView()
        self.dock_folders = QDockWidget("Folders")
        self.dock_folders.setWidget(self.folders)
        self.fileSystem = QFileSystemModel()
        self.folder_path = os.getcwd().replace("\\", '/') + "/data/folders/"
        os.makedirs(self.folder_path, exist_ok=True)
        self.fileSystem.setRootPath(self.folder_path)
        self.fileSystem.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.folders.setModel(self.fileSystem)
        self.folders.setRootIndex(self.fileSystem.index(self.folder_path))
        self.folders.setHeaderHidden(True)
        for column in range(1, self.fileSystem.columnCount()):
            self.folders.setColumnHidden(column, True)
        # endregion
       
        # region Browser View
        self.browser = QListView()
        browserToggles = QToolBar()
        thumbs = QAction(QIcon("icons/thumbs.png"),"", self)
        details = QAction(QIcon("icons/details.png"),"", self)
        browserToggles.addAction(thumbs)
        browserToggles.addAction(details)
        browserToggles.widgetForAction(thumbs).setFixedSize(21,21)
        browserToggles.widgetForAction(details).setFixedSize(21,21)
        browserToggles.setContentsMargins(0, 0, 0, 0)
        browserToggles.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        browserLayout = QVBoxLayout()
        browserLayout.addWidget(self.browser)
        browserLayout.addWidget(browserToggles)
        browserLayout.setContentsMargins(0, 0, 0, 0)
        browserLayout.setSpacing(0)
        self.browserView = QWidget()
        self.browserView.setLayout(browserLayout)
        self.dock_browser = QDockWidget("Browser")
        self.dock_browser.setWidget(self.browserView)
        # endregion

        # region Media View
        self.media = QLabel()
        mediaLayout = QVBoxLayout()
        mediaLayout.addWidget(self.media)
        mediaLayout.addWidget(QLabel("Tags and Values"))
        mediaLayout.setContentsMargins(0, 0, 0, 0)
        mediaView = QWidget()
        mediaView.setLayout(mediaLayout)
        self.dock_media = QDockWidget("Media")
        self.dock_media.setWidget(mediaView)
        # endregion

        # region Docking
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dock_search)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_folders)
        self.splitDockWidget(self.dock_folders, self.dock_browser, Qt.Orientation.Horizontal)
        self.splitDockWidget(self.dock_browser, self.dock_media, Qt.Orientation.Horizontal)
        # endregion
        
        # region Setup
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.show()
        # endregion

    def add_folder(self):
        path = QFileDialog.getExistingDirectory(self, 
			"Select Folder to Add to View", os.path.expanduser("~"))
        target = self.folder_path + os.path.basename(path)
        if os.path.exists(target):
            self.status.showMessage(f"Folder already exists - {path}")
            return
        os.symlink(path, target, target_is_directory=True)
        self.status.showMessage(f"Added - {path}")

    def open_file(self):  # DEV
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "")
        if file_path:
            if file_path.endswith(".gif") or file_path.endswith(".webp"):
                movie = QMovie(file_path)
                self.media.setMovie(movie)
                movie.start()
            else:
                pixmap = QPixmap(file_path)
                self.media.setPixmap(pixmap)

    def search(self):
        self.status.showMessage(f"Searching - {self.search_bar.text()}")

    def show_about(self):
        self.about = AboutWindow()
        self.about.show()


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Goodbye World"))
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
