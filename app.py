import sys, os, pathlib, sqlite3
from PyQt6.QtCore import Qt, QSize, QDir, QSize, QUrl
from PyQt6.QtGui import QFileSystemModel, QPixmap, QMovie, QIcon,  QAction, QImage
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
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
    QListWidget,
    QDockWidget,
    QToolBar,
    QGridLayout,
    QScrollArea,
    QSplitter
)


class SQLiteDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def execute_query_from_file(self, file_path):
        if not os.path.isfile(file_path):
            raise ValueError("File path is not valid.")
        with open(file_path, "r") as f:
            queries = f.read().split(";")
            for query in queries:
                query = query.strip()
                if query:
                    self.execute_query(query)

    def execute_query(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def fetch_data(self, query):
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


class MainWindow(QMainWindow):
    def __init__(self):

        self.filetype_switcher = {
            ".png": self.display_static,
            ".jpg": self.display_static,
            ".ico": self.display_static,
            ".svg": self.display_static,
            ".tif": self.display_static,
            ".jpeg": self.display_static,
            ".tiff": self.display_static,
            ".gif": self.display_animated,
            ".webp": self.display_animated,
            ".mp4": self.display_video,
            ".mkv": self.display_video,
            ".avi": self.display_video,
            ".mov": self.display_video,
            ".wmv": self.display_video,
            ".flv": self.display_video,
            ".mpg": self.display_video,
            ".m4v": self.display_video,
            ".3gp": self.display_video,
            ".webm": self.display_video,
            ".mpeg": self.display_video,
        }

        # region Setup
        super().__init__()
        self.setWindowTitle("Media Magic")
        # self.db = SQLiteDB("data/database.db")
        # self.db.execute_query_from_file("data/create_db.sql")
        self.resize(QSize(800, 500))
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
        self.action_addFolder.setShortcut("Ctrl+Shift+A")

        self.menu_help = self.menu_bar.addMenu("Help")
        self.action_about = self.menu_help.addAction("About Media Magic")
        self.action_about.setStatusTip("Know more about this software")
        self.action_about.triggered.connect(self.show_about)
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
        import shutil
        shutil.rmtree(self.folder_path) #DEV 
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
        self.browser_detailview = QListWidget()
        # self.browser_thumbnails = QGridLayout()
        self.browser_detailview.itemSelectionChanged.connect(self.display_media)
        browser = QWidget()
        # browserToggles = QToolBar()
        # detailview = QAction(QIcon("icons/details.png"),"", self, checkable=True, checked=True)
        # thumbnails = QAction(QIcon("icons/thumbs.png"),"", self, checkable=True)
        # detailview.toggled.connect(lambda checked: self.toggle_view(detailview, thumbnails, checked, False))
        # thumbnails.toggled.connect(lambda checked: self.toggle_view(thumbnails, detailview, checked, True))
        # browserToggles.addAction(detailview)
        # browserToggles.addAction(thumbnails)
        # browserToggles.widgetForAction(detailview).setFixedSize(21,21)
        # browserToggles.widgetForAction(thumbnails).setFixedSize(21,21)
        # browserToggles.setContentsMargins(0, 0, 0, 0)
        # browserToggles.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        browserLayout = QVBoxLayout()
        browser.setLayout(browserLayout)
        # grid = QWidget()
        # grid.setLayout(self.browser_thumbnails)
        # scroll_area = QScrollArea(self)
        # scroll_area.setWidgetResizable(True)
        # scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scroll_area.setWidget(grid)
        browserLayout.addWidget(self.browser_detailview)
        # browserLayout.addWidget(scroll_area)
        # browserLayout.addLayout(self.browser_thumbnails)
        # browserLayout.addWidget(browserToggles)
        browserLayout.setContentsMargins(0, 0, 0, 0)
        browserLayout.setSpacing(0)
        self.browserView = QWidget()
        self.browserView.setLayout(browserLayout)
        self.dock_browser = QDockWidget("Browser")
        self.dock_browser.setWidget(self.browserView)
        # endregion

        # region Media View
        self.image = QLabel()
        self.video = QVideoWidget()
        self.video.hide()
        mediaLayout = QVBoxLayout()
        mediaLayout.addWidget(self.image)
        mediaLayout.addWidget(self.video)
        mediaLayout.setContentsMargins(0, 0, 0, 0)
        media_view = QWidget()
        media_view.setLayout(mediaLayout)
        self.dock_media = QDockWidget("Media")
        self.dock_media.setWidget(media_view)
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video)
        # self.resizeEvent = self.update_size
        # endregion

        # region Tags View
        self.tags = QListWidget()
        self.dock_tags = QDockWidget("Tags")
        self.dock_tags.setWidget(self.tags)
        # endregion 

        # region Docking
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dock_search)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_folders)
        self.splitDockWidget(self.dock_folders, self.dock_browser, Qt.Orientation.Horizontal)
        self.splitDockWidget(self.dock_browser, self.dock_media, Qt.Orientation.Horizontal)
        self.splitDockWidget(self.dock_media, self.dock_tags, Qt.Orientation.Vertical)
        self.dock_folders.setMinimumWidth(150)
        self.dock_browser.setMinimumWidth(300)
        # self.dock_media.setMinimumWidth(200)
        # endregion
        
        # region Setup
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.show()
        # endregion

    # def toggle_view(self, button, other, checked, thumb):
    #     if checked:
    #         button.setChecked(True)
    #         other.setChecked(False)
    #     else:
    #         button.setChecked(False)
    #         other.setChecked(True)
    #     if thumb:
    #         self.browser_detailview.hide()
    #         for i in range(self.browser_thumbnails.count()):
    #             widget = self.browser_thumbnails.itemAt(i).widget()
    #             widget.show()
    #     else:
    #         self.browser_detailview.show()
    #         for i in range(self.browser_thumbnails.count()):
    #             widget = self.browser_thumbnails.itemAt(i).widget()
    #             widget.hide()
        
    
    def add_folder(self):
        path = QFileDialog.getExistingDirectory(self, 
			"Select Folder to Add to View", os.path.expanduser("~"))
        target = self.folder_path + os.path.basename(path)
        if os.path.exists(target):
            self.status.showMessage(f"Folder already exists - {path}")
            return
        os.symlink(path, target, target_is_directory=True)
        files = [os.path.join(root, f) for root, dir, file in os.walk(path) for f in file]
        self.browser_detailview.addItems(files)
        # for i, file in enumerate(files):
            # widget = QWidget()
            # layout = QVBoxLayout()
            # thumbnail = QLabel()
            # thumbnail.setPixmap(QPixmap(file).scaledToWidth(200))
            # layout.addWidget(thumbnail)
            # layout.addWidget(QLabel(os.path.basename(file)))
            # widget.setLayout(layout)
            # self.browser_thumbnails.addWidget(widget, i // 4, i % 4)
        self.status.showMessage(f"Added - {path}")

    def display_media(self):
        file_path = self.browser_detailview.currentItem().text()
        _, extension = os.path.splitext(file_path)
        if extension in self.filetype_switcher:
            self.filetype_switcher[extension](file_path)
        else:
            self.status.showMessage(f"Unsupported file type - {extension}")

    def display_static(self, file_path):
        self.media_player.stop()
        self.image.show()
        self.video.hide()
        self.image.setPixmap(QPixmap(file_path).scaled(self.dock_media.size() * 0.9, Qt.AspectRatioMode.KeepAspectRatio))
    
    def display_animated(self, file_path):
        self.media_player.stop()
        self.image.show()
        self.video.hide()
        movie = QMovie(file_path)
        movie.setScaledSize(QPixmap(file_path).scaled(self.dock_media.size() * 0.9, Qt.AspectRatioMode.KeepAspectRatio).size())
        self.image.setMovie(movie)
        movie.start()
    
    def display_video(self, file_path):
        self.image.hide()
        self.video.show()
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_player.play()

    # def update_size(self, event=None):
        # self.image.setPixmap(QPixmap.fromImage(self.image.scaled(self.dock_media.size(), Qt.AspectRatioMode.KeepAspectRatio)))

    def search(self):
        self.status.showMessage(f"Searching - {self.search_bar.text()}")

    def show_about(self):
        self.about = AboutWindow()
        self.about.show()
        
    # region SQL
    def add_new_tag(self, tag):
        self.db.execute_query(f"INSERT INTO Tags (name) VALUES ('{tag}')")

    def edit_tag(self, tag, new_tag):
        self.db.execute_query(f"UPDATE Tags SET name = '{new_tag}' WHERE name = '{tag}'")

    def delete_tag(self, tag):
        self.db.execute_query(f"DELETE FROM Tags WHERE name = '{tag}'")
        # Select id of that tag and then remove all filetags with that id
    
    def add_file(self, file):
        self.db.execute_query(f"INSERT INTO Files (path) VALUES ('{file}')")

    def add_tag_to_file(self, tag, file):
        query = f"""INSERT OR IGNORE INTO Tags (name) VALUES ('{tag}');
                    INSERT INTO FileTags (file_id, tag_id) VALUES 
                    (
                        (SELECT id FROM Files WHERE path = '{file}'),
                        (SELECT id FROM Tags WHERE name = '{tag}')
                    );"""
        self.db.execute_query(query)

    def remove_tag_from_file(self, tag, file):
        query = f"""DELETE FROM FileTags WHERE file_id = (SELECT id FROM Files WHERE path = '{file}')
                    AND tag_id = (SELECT id FROM Tags WHERE name = '{tag}')"""
        self.db.execute_query(query)
    
    def get_all_files(self):
        return self.db.fetch_data("SELECT * FROM Files")

    def get_file_tags(self, file):
        query = f"""SELECT t.name FROM FileTags ft
                        JOIN Files f
                            ON ft.file_id = f.id 
                        JOIN Tags t 
                            ON ft.tag_id = t.id 
                        WHERE f.path = '{file}'"""
        return self.db.fetch_data(query)
    
    def search(self, tags):
        query = f"""SELECT DISTINCT f.path FROM Files f
                        JOIN FileTags ft
                            ON f.id = ft.file_id
                        JOIN Tags t
                            ON ft.tag_id = t.id
                        WHERE t.name = '{tags[0]}'"""
        for tag in tags[1:]:
            query += f" OR t.name = '{tag}'"
        return self.db.fetch_data(query)
    # endregion

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
