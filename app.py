import sys, os, sqlite3, face_recognition, threading, random, numpy as np, base64, shutil
from PyQt6.QtCore import Qt, QSize, QDir, QSize, QUrl, QSortFilterProxyModel, QMargins
from PyQt6.QtGui import QFileSystemModel, QPixmap, QMovie, QIcon, QAction, QStandardItemModel, QStandardItem
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QStyle,
    QSlider,
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
    QAbstractItemView,
    QListView,
    QMenu,
    QListWidgetItem,
    QSpacerItem,
)


class SQLiteDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

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
        self.conn.execute(query)
        self.conn.commit()

    def fetch_data(self, query):
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def close_connection(self):
        self.conn.close()


class QDeselectableListWidget(QListWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QListWidget.mousePressEvent(self, event)


class QDeselectableTreeView(QTreeView):
    # def __init__(self, parent=None):
    # super().__init__(parent)
    # self.other_func = lambda: None

    def mousePressEvent(self, event):
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)
        # self.other_func()

    # def setOtherFunction(self, func):
    # self.other_func = func


class QDetailListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.model = QStandardItemModel()
        self.setModel(self.model)

        self.sort_proxy_model = QSortFilterProxyModel()
        self.sort_proxy_model.setSourceModel(self.model)
        self.sort_proxy_model.setSortRole(Qt.ItemDataRole.DisplayRole)
        self.sort_proxy_model.sort(0, Qt.SortOrder.AscendingOrder)
        self.setBatchSize(2000)

        self.setModel(self.sort_proxy_model)

        self.items = set()
        self.index_map = {}

    def get_len(self):
        return len(self.items)

    def setSelectionChangedFunction(self, func):
        self.selectionModel().selectionChanged.connect(func)

    def get_selected_text(self):
        index = self.currentIndex()
        if index.isValid():
            item = self.model.itemFromIndex(self.sort_proxy_model.mapToSource(index))
            return item.text()
        else:
            return None

    # def add_strings(self, string_list):
    #     for string in [s for s in string_list if s not in self.items]:
    #         self.items.add(string)
    #         self.model.appendRow(QStandardItem(string))
    def add_strings(self, string_list):
        for string in [s for s in string_list if s not in self.items]:
            self.items.add(string)
            item = QStandardItem(string)
            row = self.model.rowCount()
            self.model.setItem(row, item)
            self.index_map[string] = row

    def remove_strings(self, string_list):
        for string in string_list:
            if string in self.items:
                self.items.remove(string)
                if string in self.index_map:
                    row = self.index_map[string]
                    self.model.removeRow(row)
                    del self.index_map[string]

    def clear(self):
        self.model.clear()
        self.items.clear()


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Goodbye World"))
        self.setLayout(layout)


# region Increase Display Count
# class QCStandardItemModel(QStandardItemModel):
#     def rowCount(self, parent=QModelIndex()):
#         return 20000

# class QCSortFilterProxyModel(QSortFilterProxyModel):
#     def rowCount(self, parent=QModelIndex()):
#         return 20000
# endregion

class MainWindow(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self):

        # region Setup
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
        self.db_path = "data/database.db"

        super().__init__()
        self.setWindowTitle("Image Search")
        self.db = SQLiteDB(self.db_path)
        self.db.execute_query_from_file("data/sql/create_db.sql")
        self.resize(QSize(800, 500))
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
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
        self.menu_file.addSeparator()
        self.action_exit = self.menu_file.addAction("Exit")
        self.action_exit.triggered.connect(self.close)

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
        self.search_bar.returnPressed.connect(self.search_enter.pressed)
        self.search_bar.setPlaceholderText(" -- Search multiple tags with spaces -- Press Esc to focus")
        self.search_enter.pressed.connect(lambda: self.search(self.search_bar.text()))
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(QIcon("icons/clear.png"))
        self.clear_btn.setShortcut("Esc")
        self.clear_btn.pressed.connect(self.clear)
        # self.ai_process_btn = QPushButton("AI Process")
        # self.ai_process_btn.pressed.connect(self.ai_process)
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.search_bar)
        searchLayout.addWidget(self.clear_btn)
        searchLayout.addWidget(self.search_enter)
        # searchLayout.addWidget(self.ai_process_btn)
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
        self.folders = QDeselectableTreeView()
        # self.folders.setOtherFunction(lambda: self.)
        self.dock_folders = QDockWidget("Folders")
        self.dock_folders.setWidget(self.folders)
        self.fileSystem = QFileSystemModel()
        self.folder_path = os.getcwd().replace("\\", '/') + "/data/folders"
        # shutil.rmtree(self.folder_path) #DEV
        os.makedirs(self.folder_path, exist_ok=True)
        self.fileSystem.setRootPath(self.folder_path)
        self.fileSystem.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.folders.setModel(self.fileSystem)
        self.folders.setRootIndex(self.fileSystem.index(self.folder_path))
        self.folders.setHeaderHidden(True)
        for column in range(1, self.fileSystem.columnCount()):
            self.folders.setColumnHidden(column, True)
        self.folders.setAnimated(True)
        self.folders.setIndentation(10)
        self.folders.setSortingEnabled(True)
        self.folders.selectionModel().selectionChanged.connect(self.folder_selected)
        self.folders.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        self.folders.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folders.customContextMenuRequested.connect(self.folder_context_menu)
        # endregion

        # region Browser View
        self.browser_detailView = QDetailListView()
        self.browser_thumbnails = QGridLayout()
        self.browser_detailView.setSelectionChangedFunction(self.display_media)
        browser = QWidget()

        browserToggles = QToolBar()
        detailview = QAction(QIcon("icons/details.png"), "", self, checkable=True, checked=True)
        thumbnails = QAction(QIcon("icons/thumbs.png"), "", self, checkable=True)
        detailview.toggled.connect(lambda checked: self.toggle_view(detailview, thumbnails, checked, False))
        thumbnails.toggled.connect(lambda checked: self.toggle_view(thumbnails, detailview, checked, True))
        browserToggles.addAction(detailview)
        browserToggles.addAction(thumbnails)
        browserToggles.widgetForAction(detailview).setFixedSize(21, 21)
        browserToggles.widgetForAction(thumbnails).setFixedSize(21, 21)
        browserToggles.setContentsMargins(0, 0, 0, 0)
        browserToggles.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        browserLayout = QVBoxLayout()
        browser.setLayout(browserLayout)
        # grid = QWidget()
        # grid.setLayout(self.browser_thumbnails)
        # scroll_area = QScrollArea(self)
        # scroll_area.setWidgetResizable(True)
        # scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scroll_area.setWidget(grid)
        browserLayout.addWidget(self.browser_detailView)

        # browserLayout.addWidget(scroll_area)
        browserLayout.addLayout(self.browser_thumbnails)
        browserLayout.addWidget(browserToggles)

        browserLayout.setContentsMargins(0, 0, 0, 0)
        browserLayout.setSpacing(0)
        self.browserView = QWidget()
        self.browserView.setLayout(browserLayout)
        self.dock_browser = QDockWidget("Browser")
        self.dock_browser.setWidget(self.browserView)
        # endregion

        # region Media View
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(60)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video = QVideoWidget()
        self.media_player.setVideoOutput(self.video)
        # self.fullscreen_button = QPushButton()
        # self.fullscreen_button.pressed.connect(lambda: self.showFullScreen())
        self.video_controls = QVBoxLayout()
        self.video_controls.setContentsMargins(2, 2, 2, 2)
        self.video_controls.setSpacing(0)
        self.play_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "", self, checkable=True)
        self.play_btn.pressed.connect(self.play)
        self.volume_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume), "", self, checkable=True)
        self.volume_btn.pressed.connect(self.mute)
        self.media_player.playbackStateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.play_btn.setFixedSize(20, 20)
        self.volume_btn.setFixedSize(20, 20)
        self.media_seeker = QSlider(Qt.Orientation.Horizontal)
        self.media_seeker.sliderMoved.connect(self.setPosition)
        self.volume_control = QSlider(Qt.Orientation.Horizontal)
        self.volume_control.setRange(0, 100)
        self.volume_control.setValue(60)
        self.volume_control.setMaximumWidth(50)
        self.volume_control.sliderMoved.connect(self.setVolume)
        self.time_tracker = QLabel(f"--:--/--:--")
        # Add media controls here
        self.othercontrols = QHBoxLayout()
        self.othercontrols.setContentsMargins(0, 0, 0, 0)
        self.othercontrols.setSpacing(5)
        self.othercontrols.addWidget(self.play_btn)
        self.othercontrols.addWidget(self.volume_btn)
        self.othercontrols.addWidget(self.volume_control)
        self.othercontrols.addWidget(self.time_tracker)
        # self.othercontrols.addWidget(self.fullscreen_button)
        self.othercontrols_widget = QWidget()
        self.othercontrols_widget.setLayout(self.othercontrols)
        self.video_controls.addWidget(self.media_seeker)
        self.video_controls.addWidget(self.othercontrols_widget)
        self.othercontrols_widget.setFixedHeight(20)
        self.videocontrols_widget = QWidget()
        self.videocontrols_widget.setLayout(self.video_controls)
        self.videocontrols_widget.setFixedHeight(40)
        self.videobox = QVBoxLayout()
        self.videobox.setContentsMargins(0, 0, 0, 0)
        self.videobox.setSpacing(0)
        self.videobox.addWidget(self.video)
        self.videobox.addWidget(self.videocontrols_widget)
        self.videobox_widget = QWidget()
        self.videobox_widget.setLayout(self.videobox)
        self.videobox_widget.hide()
        mediaLayout = QVBoxLayout()
        mediaLayout.addWidget(self.image)
        mediaLayout.addWidget(self.videobox_widget)
        mediaLayout.setContentsMargins(0, 0, 0, 0)
        media_view = QWidget()
        media_view.setLayout(mediaLayout)
        self.dock_media = QDockWidget("Media")
        self.dock_media.setWidget(media_view)
        # self.resizeEvent = self.update_size
        # endregion

        # region Tags View
        self.dock_tags = QDockWidget("Tags")
        self.tags = QListWidget()
        self.tags.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.tags.itemDoubleClicked.connect(self.tag_double_clicked)
        self.tags.itemChanged.connect(self.tag_update)
        self.tag_bar = QLineEdit()
        self.tag_bar.setPlaceholderText("Press Ctrl+T to focus")
        btn_add_tag = QPushButton("Add Tag")
        tagBarLayout = QHBoxLayout()
        tagBarLayout.setContentsMargins(0, 0, 0, 0)
        tagBarLayout.setSpacing(0)
        tagBarLayout.addWidget(self.tag_bar)
        tagBarLayout.addWidget(btn_add_tag)
        tagBarWidget = QWidget()
        tagBarWidget.setLayout(tagBarLayout)
        btn_add_tag.pressed.connect(
            lambda: self.add_tag_to_file(self.tag_bar.text(), self.browser_detailView.get_selected_text()))
        self.tag_bar.returnPressed.connect(btn_add_tag.pressed)
        self.tag_bar_shortcut = QPushButton()
        self.tag_bar_shortcut.setShortcut("Ctrl+T")
        self.tag_bar_shortcut.pressed.connect(lambda: self.tag_bar.setFocus())
        tagBarLayout.addWidget(self.tag_bar_shortcut)
        self.tag_bar_shortcut.setFixedSize(0, 0)
        tag_view = QWidget()
        tagLayout = QVBoxLayout()
        tagLayout.addWidget(self.tags)
        tagLayout.addWidget(tagBarWidget)
        tagLayout.setContentsMargins(0, 0, 0, 0)
        tagLayout.setSpacing(0)
        tag_view.setLayout(tagLayout)
        self.dock_tags.setWidget(tag_view)
        # endregion 

        # region People View
        self.dock_people = QDockWidget("People")
        self.people = QListWidget()
        self.people.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # self.people.selectionModel().selectionChanged.connect(self.people_selected)
        self.people.itemSelectionChanged.connect(self.people_selected)
        people_view = QWidget()
        peopleLayout = QVBoxLayout()
        people_view.setLayout(peopleLayout)
        peopleLayout.addWidget(self.people)
        peopleLayout.setContentsMargins(0, 0, 0, 0)
        peopleLayout.setSpacing(0)
        self.dock_people.setWidget(people_view)
        self.people.addItems(self.sql_get_all_people())
        # endregion

        # region Docking
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dock_search)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_folders)
        self.splitDockWidget(self.dock_folders, self.dock_browser, Qt.Orientation.Horizontal)
        self.splitDockWidget(self.dock_browser, self.dock_media, Qt.Orientation.Horizontal)
        self.splitDockWidget(self.dock_media, self.dock_tags, Qt.Orientation.Vertical)
        self.splitDockWidget(self.dock_folders, self.dock_people, Qt.Orientation.Vertical)
        self.dock_folders.setMinimumWidth(150)
        self.dock_browser.setMinimumWidth(300)
        # self.dock_media.setMinimumWidth(200)
        # endregion

        # region Setup
        self.folder_selected()
        # self.people_selected()
        self.editing = False
        self.old_tag = ""
        threading.Thread(target=self.update_folders).start()
        self.show()
        # endregion

    # region Mechanics
    def update_folders(self):
        old = self.sql_get_all_files()
        folders = self.sql_get_all_folders()
        new = [self.file_op(os.path.join(folder, file)) for folder in folders for file in os.listdir(folder) if
               os.path.isfile(os.path.join(folder, file))]
        difference = len(new) - len(old)
        if difference != 0:
            self.status.showMessage(f"Found {difference} file changes")
            new_files = [self.file_op(x) for x in new if x not in old]
            deleted_files = [self.file_op(x) for x in old if x not in new]
            self.sql_add_files(new_files)
            self.sql_delete_files(deleted_files)
            self.browser_detailView.add_strings(new_files)
            self.browser_detailView.remove_strings(deleted_files)
            self.status.showMessage(f"Added {len(new_files)} files and removed {len(deleted_files)} files")

    def tag_double_clicked(self):
        self.editing = True
        self.old_tag = self.tags.selectedItems()[0].text()

    def tag_update(self):
        if self.editing:
            self.editing = False
            new_tag = self.tags.selectedItems()[0].text()
            self.status.showMessage(f"Tag Updated from {self.old_tag} to {new_tag}")
            self.sql_edit_tag(self.old_tag, new_tag)
            if self.old_tag in [self.people.item(x).text() for x in range(self.people.count())]:
                self.people.clear()
                self.people.addItems(self.sql_get_all_people())

    def people_selected(self):
        self.browser_detailView.clear()
        if len(self.people.selectedIndexes()) == 0:
            self.browser_detailView.add_strings(self.sql_get_all_files())
            self.update_title("Browser")
        else:
            person = self.people.currentItem().text()
            self.status.showMessage(f"Searching for person - {person}")
            self.browser_detailView.add_strings(self.sql_search_inclusive([person]))
            self.update_title(person)

    def folder_context_menu(self, pos):
        menu = QMenu()
        action_add_folder = QAction("Add Folder\tCtrl+Shift+A", self)
        action_add_folder.triggered.connect(self.add_folder)
        action_recognize_people = QAction("Recognize People", self)
        action_recognize_people.triggered.connect(lambda: threading.Thread(target=self.ai_recognize_people).start())
        menu.addAction(action_add_folder)
        menu.addSeparator()
        menu.addAction(action_recognize_people)
        menu.exec(self.folders.viewport().mapToGlobal(pos))

    def clear(self):
        self.search_bar.clear()
        self.tag_bar.clear()
        self.search_bar.setFocus()
        self.folders.clearSelection()
        self.folder_selected()

    def update_title(self, title):
        self.dock_browser.setWindowTitle(f'{title} - {self.browser_detailView.get_len()} items')

    def toggle_view(self, button, other, checked, thumb):
        if checked:
            button.setChecked(True)
            other.setChecked(False)
        else:
            button.setChecked(False)
            other.setChecked(True)
        # if thumb:
        #     self.browser_detailview.hide()
        #     for i in range(self.browser_thumbnails.count()):
        #         widget = self.browser_thumbnails.itemAt(i).widget()
        #         widget.show()
        # else:
        #     self.browser_detailview.show()
        #     for i in range(self.browser_thumbnails.count()):
        #         widget = self.browser_thumbnails.itemAt(i).widget()
        #         widget.hide()

    def folder_selected(self):
        self.browser_detailView.clear()
        if len(self.folders.selectedIndexes()) == 0:
            self.browser_detailView.add_strings(self.sql_get_all_files())
            self.update_title("Browser")
        else:
            for index in self.folders.selectedIndexes():
                sym_path = self.fileSystem.filePath(index)
                org_path = self.sql_get_files_in_folder(sym_path)
                self.browser_detailView.add_strings(
                    [f'{self.file_op(root)}/{f}' for root, dir, file in os.walk(org_path) for f in file])
            self.update_title(self.folders.selectedIndexes()[0].data())

    def file_op(self, f):
        return f.replace('\\', '/')

    def add_folder(self):
        path = QFileDialog.getExistingDirectory(self,
                                                "Select Folder to Add to View", os.path.expanduser("~"))
        target = f'{self.folder_path}/{os.path.basename(path)}'
        self.folder_path = os.path.dirname(target)
        if os.path.exists(target):
            self.status.showMessage(f"Folder already exists - {path}")
            return
        os.symlink(path, target, target_is_directory=True)
        files = [f'{self.file_op(root)}/{f}' for root, dir, file in os.walk(path) for f in file]
        self.browser_detailView.add_strings(files)
        self.sql_add_folder(path, target)
        for subfolder in [f'{root}/{d}'[len(path) + 1:].replace('\\', '/') for root, dirs, files in os.walk(path) for d
                          in dirs]:
            self.sql_add_folder(f'{path}/{subfolder}', f'{target}/{subfolder}')
        self.sql_add_files(files)
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

    def add_tag_to_file(self, tag, file):
        if self.sql_check_tag_exists(file, tag):
            self.status.showMessage(f"Tag already exists on media file {file} - {tag}")
            return
        self.sql_add_tag_to_file(tag, file)
        item = QListWidgetItem(tag)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.tags.addItem(item)
        self.status.showMessage(f"Added tag - {tag} to file - {file}")

    def search(self, tags):
        tagList = list(set(tags.split(" ")))
        tagString = ', '.join(tagList)
        self.status.showMessage(f"Searching for files with tags - {tagString}")
        self.browser_detailView.clear()
        self.browser_detailView.add_strings(self.sql_search_inclusive(tagList))
        self.update_title(tagString)

    def generate_random_person_name(self):
        return f'person_{random.randint(10000, 99999)}'

    def add_person(self, unique_people, encoding, file):
        result = face_recognition.compare_faces(unique_people, encoding)
        check = np.count_nonzero(result)
        if check == 0:
            name = self.generate_random_person_name()
            self.sql_add_face_encoding(name, encoding)
            self.people.addItem(name)
            self.new_people += 1
        elif check == 1:
            name = self.sql_get_person_name(unique_people[result.index(True)])
        elif check > 1:
            distances = face_recognition.face_distance(unique_people, encoding)
            name = self.sql_get_person_name(unique_people[np.argmin(distances)])
        self.sql_add_tag_to_file(name, file)
        self.tags_applied += 1
        return True if check == 0 else False

    def ai_recognize_people(self):
        self.tags_applied = 0
        self.new_people = 0
        unique_people = self.sql_get_all_encodings()
        for index in self.folders.selectedIndexes():
            sym_path = self.fileSystem.filePath(index)
            org_path = self.sql_get_files_in_folder(sym_path)
            for file in [f'{self.file_op(root)}/{f}' for root, dir, file in os.walk(org_path) for f in file]:
                self.status.showMessage(f"AI Processing - {file}")
                _, extension = os.path.splitext(file)
                if self.filetype_switcher[extension].__name__ != self.display_static.__name__:
                    continue
                image = face_recognition.load_image_file(file)
                face_encodings = face_recognition.face_encodings(image, num_jitters=5, model="large")
                if len(face_encodings) > 0:
                    for encoding in face_encodings:
                        if self.add_person(unique_people, encoding, file):
                            unique_people.append(encoding)
        self.status.showMessage(
            f"AI Processing - {org_path} - Finished - Applied {self.tags_applied} tags - Detected {self.new_people} new people")

    def show_about(self):
        self.about = AboutWindow()
        self.about.show()

    # endregion

    # region Media Controls
    def play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def ms_to_mmss(self, milliseconds):
        minutes, seconds = divmod(milliseconds // 1000, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def positionChanged(self, position):
        self.media_seeker.setValue(position)
        self.time_tracker.setText(
            f'{self.ms_to_mmss(self.media_player.position())}/{self.ms_to_mmss(self.media_player.duration())}')

    def durationChanged(self, duration):
        self.media_seeker.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)

    def setVolume(self):
        volume = self.volume_control.value() / 100
        self.audio_output.setVolume(volume)

    def mute(self):
        isMuted = self.audio_output.isMuted()
        self.audio_output.setMuted(not isMuted)
        if not isMuted:
            self.volume_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))

    # endregion

    # region Display Media
    def display_media(self):
        file_path = self.browser_detailView.get_selected_text()
        _, extension = os.path.splitext(file_path)
        if extension in self.filetype_switcher:
            self.filetype_switcher[extension](file_path)
            self.dock_media.setWindowTitle(f'Media - {file_path}')
            self.tags.clear()
            tags = self.sql_get_file_tags(file_path)
            for tag in tags:
                item = QListWidgetItem(tag, self.tags)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.tags.addItem(item)
        else:
            self.status.showMessage(f"Unsupported file type - {extension}")

    def display_static(self, file_path):
        self.media_player.stop()
        self.image.show()
        self.videobox_widget.hide()
        self.image.setPixmap(
            QPixmap(file_path).scaled(self.dock_media.size() * 0.95, Qt.AspectRatioMode.KeepAspectRatio))

    def display_animated(self, file_path):
        self.media_player.stop()
        self.image.show()
        self.videobox_widget.hide()
        movie = QMovie(file_path)
        movie.setScaledSize(
            QPixmap(file_path).scaled(self.dock_media.size() * 0.95, Qt.AspectRatioMode.KeepAspectRatio).size())
        self.image.setMovie(movie)
        movie.start()

    def display_video(self, file_path):
        self.image.hide()
        self.videobox_widget.show()
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.media_player.play()

    # endregion

    # region SQL
    def sql_get_all_folders(self):
        return [x[0] for x in self.db.fetch_data(f"SELECT f.org_path FROM Folders f")]

    def sql_add_new_tag(self, tag):
        self.db.execute_query(f"INSERT OR IGNORE INTO Tags (name) VALUES ('{tag}')")

    def sql_edit_tag(self, tag, new_tag):
        self.db.execute_query(f"UPDATE Tags SET name = '{new_tag}' WHERE name = '{tag}'")
        self.db.execute_query(f"UPDATE People SET name = '{new_tag}' WHERE name = '{tag}'")

    def sql_delete_tag(self, tag):
        self.db.execute_query(f"DELETE FROM Tags WHERE name = '{tag}'")
        # Select id of that tag and then remove all filetags with that id

    def sql_add_folder(self, folder, sym_path):
        self.db.execute_query(f"INSERT INTO Folders (org_path, sym_path) VALUES ('{folder}', '{sym_path}')")

    def sql_add_files(self, files):
        for file in files:
            self.db.execute_query(f"INSERT INTO Files (path) VALUES ('{file}')")

    def sql_delete_files(self, files):
        for file in files:
            self.db.execute_query(f"DELETE FROM Files WHERE path = '{file}'")

    def sql_add_tag_to_file(self, tag, file):
        self.sql_add_new_tag(tag)
        query = f"""INSERT OR IGNORE INTO FileTags (file_id, tag_id) VALUES 
                    (
                        (SELECT id FROM Files WHERE path = '{file}'),
                        (SELECT id FROM Tags WHERE name = '{tag}')
                    );"""
        self.db.execute_query(query)

    def sql_remove_tag_from_file(self, tag, file):
        query = f"""DELETE FROM FileTags WHERE file_id = (SELECT id FROM Files WHERE path = '{file}')
                    AND tag_id = (SELECT id FROM Tags WHERE name = '{tag}')"""
        self.db.execute_query(query)

    def sql_get_all_files(self):
        return [x[0] for x in self.db.fetch_data("SELECT f.path FROM Files f")]

    def sql_get_files_in_folder(self, sym_path):
        return self.db.fetch_data(f"SELECT f.org_path FROM Folders f WHERE sym_path = '{sym_path}'")[0][0]

    def sql_get_file_tags(self, file):
        query = f"""SELECT t.name FROM FileTags ft
                        JOIN Files f
                            ON ft.file_id = f.id 
                        JOIN Tags t 
                            ON ft.tag_id = t.id 
                        WHERE f.path = '{file}'"""
        return [x[0] for x in self.db.fetch_data(query)]

    def sql_check_tag_exists(self, file, tag):
        tags = self.db.fetch_data(
            f"SELECT t.name FROM Tags t JOIN FileTags ft ON  t.id = ft.tag_id JOIN Files f ON ft.file_id = f.id WHERE f.path = '{file}'")
        return tag in [x[0] for x in tags]

    def sql_search_inclusive(self, tags):
        query = f"""SELECT DISTINCT f.path FROM Files f
                        JOIN FileTags ft
                            ON f.id = ft.file_id
                        JOIN Tags t
                            ON ft.tag_id = t.id
                        WHERE t.name = '{tags[0]}'"""
        for tag in tags[1:]:
            query += f" OR t.name = '{tag}'"
        return [x[0] for x in self.db.fetch_data(query)]

    def sql_add_face_encoding(self, name, encoding):
        enc = base64.binascii.b2a_base64(encoding).decode("ascii")
        self.db.execute_query(f"INSERT OR IGNORE INTO People (name, encoding) VALUES ('{name}', '{enc}')")

    def sql_get_all_encodings(self):
        return [np.frombuffer(base64.binascii.a2b_base64(x[0].encode("ascii"))) for x in
                self.db.fetch_data("SELECT encoding FROM People")]

    def sql_get_person_name(self, encoding):
        enc = base64.binascii.b2a_base64(encoding).decode("ascii")
        return self.db.fetch_data(f"SELECT name FROM People WHERE encoding = '{enc}'")[0][0]

    def sql_get_all_people(self):
        return [x[0] for x in self.db.fetch_data("SELECT name FROM People")]
    # endregion


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
