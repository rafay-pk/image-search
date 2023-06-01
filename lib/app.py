import sys, os, face_recognition, threading, random, numpy as np, database, widgets, caption, re
from collections import Counter
from PyQt6.QtCore import Qt, QSize, QDir, QSize, QUrl
from PyQt6.QtGui import QFileSystemModel, QPixmap, QMovie, QIcon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
	QAbstractItemView,
	QApplication,
	QCheckBox,
	QDockWidget,
	QFileDialog,
	QGridLayout,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QListWidget,
	QListWidgetItem,
	QMainWindow,
	QMenu,
	QPushButton,
	QSlider,
	QStatusBar,
	QStyle,
	QToolBar,
	QVBoxLayout,
	QWidget,
)

def list_files(folder):
	return [f"{root.replace(chr(92), '/')}/{f}" for root, _, file in os.walk(folder) for f in file]

def generate_random_person_name():
	while True:
		name = f'person_{random.randint(10000, 99999)}'
		if name not in db.get_all_people():
			return name

class MainWindow(QMainWindow):
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

		super().__init__()
		self.setWindowTitle("Image Search")
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
		self.search_toggle = QCheckBox("Include Captions")
		# self.ai_process_btn = QPushButton("AI Process")
		# self.ai_process_btn.pressed.connect(self.ai_process)
		searchLayout = QHBoxLayout()
		searchLayout.addWidget(self.search_bar)
		searchLayout.addWidget(self.search_toggle)
		searchLayout.addWidget(self.clear_btn)
		searchLayout.addWidget(self.search_enter)
		# searchLayout.addWidget(self.ai_process_btn)
		searchLayout.setContentsMargins(0, 0, 0, 0)
		searchLayout.setSpacing(5)
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
		self.folders = widgets.QDeselectableTreeView()
		self.dock_folders = QDockWidget("Folders")
		self.dock_folders.setWidget(self.folders)
		self.fileSystem = QFileSystemModel()
		self.folder_path = os.getcwd().replace("\\", '/') + "/data/folders"
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
		self.browser_detailView = widgets.QDetailListView()
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
		self.play_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "", self,
									checkable=True)
		self.play_btn.pressed.connect(self.play)
		self.volume_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume), "", self,
									  checkable=True)
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
		self.caption_image = QLabel()
		self.caption_image.setVisible(False)
		self.caption_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.caption_image.setFixedHeight(30)
		# imageLayout = QVBoxLayout()
		# imageLayout.setContentsMargins(0, 0, 0, 0)
		# imageLayout.setSpacing(0)
		# imageLayout.addWidget(self.image)
		# imageLayout.addWidget(self.caption_image)
		# self.image_widget = QWidget()
		# self.image_widget.setLayout(imageLayout)
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
		self.dock_tags = QDockWidget("Data")
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
		tagLayout.addWidget(self.caption_image)
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
		self.people.addItems(db.get_all_people())
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
		####### self.people_selected()
		self.editing = False
		self.old_tag = ""
		threading.Thread(target=self.update_folders).start()
		self.show()
		self.captioner = caption.ImageCaptioner()
		# endregion

	# region Mechanics
	def update_folders(self):
		old = db.get_all_files()
		folders = db.get_all_folders()
		new = [self.file_op(os.path.join(folder, file)) for folder in folders for file in os.listdir(folder) if
			   os.path.isfile(os.path.join(folder, file))]
		difference = len(new) - len(old)
		if difference != 0:
			self.status.showMessage(f"Found {difference} file changes")
			new_files = [self.file_op(x) for x in new if x not in old]
			deleted_files = [self.file_op(x) for x in old if x not in new]
			db.add_files(new_files)
			db.delete_files(deleted_files)
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
			db.edit_tag(self.old_tag, new_tag)
			if self.old_tag in [self.people.item(x).text() for x in range(self.people.count())]:
				self.people.clear()
				self.people.addItems(db.get_all_people())

	def people_selected(self):
		self.browser_detailView.clear()
		if len(self.people.selectedIndexes()) == 0:
			self.browser_detailView.add_strings(db.get_all_files())
			self.update_title("Browser")
		else:
			person = self.people.currentItem().text()
			self.status.showMessage(f"Searching for person - {person}")
			self.browser_detailView.add_strings(db.search_inclusive([person]))
			self.update_title(person)

	def folder_context_menu(self, pos):
		menu = QMenu()
		action_add_folder = QAction("Add Folder\tCtrl+Shift+A", self)
		action_add_folder.triggered.connect(self.add_folder)
		action_recognize_people = QAction("Recognize People", self)
		action_recognize_people.triggered.connect(lambda: threading.Thread(target=self.ai_recognize_people).start())
		action_caption_images = QAction("Caption Images", self)
		action_caption_images.triggered.connect(lambda: threading.Thread(target=self.ai_caption_images).start())
		menu.addAction(action_add_folder)
		menu.addSeparator()
		menu.addAction(action_recognize_people)
		menu.addAction(action_caption_images)
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
			self.browser_detailView.add_strings(db.get_all_files())
			self.update_title("Browser")
		else:
			for index in self.folders.selectedIndexes():
				sym_path = self.fileSystem.filePath(index)
				org_path = db.get_files_in_folder(sym_path)
				self.browser_detailView.add_strings(list_files(org_path))
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
		db.add_folder(path, target)
		for subfolder in [f'{root}/{d}'[len(path) + 1:].replace('\\', '/') for root, dirs, files in os.walk(path) for d
						  in dirs]:
			db.add_folder(f'{path}/{subfolder}', f'{target}/{subfolder}')
		db.add_files(files)
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
		if db.check_tag_exists(file, tag):
			self.status.showMessage(f"Tag already exists on media file {file} - {tag}")
			return
		db.add_tag_to_file(tag, file)
		item = QListWidgetItem(tag)
		item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
		self.tags.addItem(item)
		self.status.showMessage(f"Added tag - {tag} to file - {file}")

	def search(self, tags):
		tagList = list(set(tags.split(" ")))
		tagString = ', '.join(tagList)
		self.status.showMessage(f"Searching for files with tags - {tagString}")
		self.browser_detailView.clear()
		files_to_add = set(db.search_inclusive(tagList))
		if self.search_toggle.isChecked():
			files_to_add.update(set([db.get_file_from_caption(x) for x in self.search_captions(tagList)]))
			# self.browser_detailView.add_strings([db.get_file_from_caption(x) for x in caption_results])
		self.browser_detailView.add_strings(files_to_add)
		self.image.clear()
		self.update_title(tagString)

	def calculate_relevance_score(self, sentence, search_words):
		tokenized_sentence = re.findall(r'\w+', sentence.lower())
		word_counts = Counter(tokenized_sentence)
		score = sum(word_counts[word] for word in search_words)
		return score

	def search_captions(self, tags):
		results = []
		for sentence in filter(None, db.get_all_captions()):
			relevance = sum(1 for keyword in tags if re.search(r'\b{}\b'.format(keyword), sentence, re.IGNORECASE))
			# relevance = self.calculate_relevance_score(sentence, tags)
			if relevance > 0:
				results.append((sentence, relevance))
		sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
		return [x[0] for x in sorted_results]

	def add_person(self, unique_people, encoding, file):
		result = face_recognition.compare_faces(unique_people, encoding)
		check = np.count_nonzero(result)
		if check == 0:
			name = generate_random_person_name()
			db.add_face_encoding(name, encoding)
			self.people.addItem(name)
			self.new_people += 1
		elif check == 1:
			name = db.get_person_name(unique_people[result.index(True)])
		elif check > 1:
			distances = face_recognition.face_distance(unique_people, encoding)
			name = db.get_person_name(unique_people[np.argmin(distances)])
		db.add_tag_to_file(name, file)
		self.tags_applied += 1
		return True if check == 0 else False

	def ai_recognize_people(self):
		self.tags_applied = 0
		self.new_people = 0
		unique_people = db.get_all_encodings()
		for index in self.folders.selectedIndexes():
			sym_path = self.fileSystem.filePath(index)
			org_path = db.get_files_in_folder(sym_path)
			for file in list_files(org_path):
				_, extension = os.path.splitext(file)
				if self.filetype_switcher[extension].__name__ != self.display_static.__name__:
					continue
				self.status.showMessage(f"AI - Recognizing Faces - {file}")
				image = face_recognition.load_image_file(file)
				locations = face_recognition.face_locations(image, 1, model='hog')
				encodings = face_recognition.face_encodings(image, locations, num_jitters=1, model='small')
				if len(encodings) > 0:
					for encoding in encodings:
						if self.add_person(unique_people, encoding, file):
							unique_people.append(encoding)
		self.status.showMessage(
			f"AI - Recognizing Faces - {org_path} - Finished - Applied {self.tags_applied} tags - Detected {self.new_people} new people")

	def ai_caption_images(self):
		for index in self.folders.selectedIndexes():
			sym_path = self.fileSystem.filePath(index)
			org_path = db.get_files_in_folder(sym_path)
			for i, file in enumerate(list_files(org_path)):
				_, extension = os.path.splitext(file)
				if self.filetype_switcher[extension].__name__ not in [self.display_static.__name__, self.display_animated.__name__] or db.get_caption(file) is not None:
					continue
				self.status.showMessage("AI - Captioning Image - Loading Model" if i == 0 else f"AI - Captioning Image - {file}")
				caption = self.captioner.predict_step(file)[0]
				db.add_caption_to_file(caption, file)
		self.status.showMessage(f"AI - Captioning Images - {org_path} - Finished")

	def show_about(self):
		self.about = widgets.AboutWindow()
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
	def update_caption(self, file_path):
		caption = db.get_caption(file_path)
		if caption:
			self.caption_image.setText(caption)
			self.caption_image.show()
		else:
			self.caption_image.hide()

	def display_media(self):
		file_path = self.browser_detailView.get_selected_text()
		_, extension = os.path.splitext(file_path)
		if extension in self.filetype_switcher:
			self.filetype_switcher[extension](file_path)
			self.dock_media.setWindowTitle(f'Media - {file_path}')
			self.tags.clear()
			tags = db.get_file_tags(file_path)
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
		self.image.setPixmap(QPixmap(file_path).scaled(self.dock_media.size() * 0.95, Qt.AspectRatioMode.KeepAspectRatio))
		self.update_caption(file_path)

	def display_animated(self, file_path):
		self.media_player.stop()
		self.image.show()
		self.videobox_widget.hide()
		movie = QMovie(file_path)
		movie.setScaledSize(
			QPixmap(file_path).scaled(self.dock_media.size() * 0.95, Qt.AspectRatioMode.KeepAspectRatio).size())
		self.image.setMovie(movie)
		movie.start()
		self.update_caption(file_path)

	def display_video(self, file_path):
		self.caption_image.hide()
		self.image.hide()
		self.videobox_widget.show()
		self.media_player.setSource(QUrl.fromLocalFile(file_path))
		self.media_player.play()
	# endregion


if __name__ == "__main__":
	db = database.DataBase()
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
