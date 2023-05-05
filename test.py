import sys
from PyQt6.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListView

class QDetailListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        
        self.model = QStandardItemModel()
        self.setModel(self.model)
        
        self.sort_proxy_model = QSortFilterProxyModel()
        self.sort_proxy_model.setSourceModel(self.model)
        self.sort_proxy_model.setSortRole(Qt.ItemDataRole.DisplayRole)
        self.sort_proxy_model.sort(0, Qt.SortOrder.AscendingOrder)
        
        self.setModel(self.sort_proxy_model)
        
        self.items = set()
        
    def setSelectionChangedFunction(self, func):
        self.selectionModel().selectionChanged.connect(func)
    
    def add_strings(self, string_list):
        for string in [s for s in string_list if s not in self.items]:
            self.items.add(string)
            self.model.appendRow(QStandardItem(string))
    
    def clear(self):
        self.model.clear()
        self.items.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Detail List View Example")
        self.setGeometry(100, 100, 500, 500)
        
        # create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # create the DetailListView object
        self.browser_detailView = DetailListView(self)
        
        # set the data of the DetailListView to an initial set of strings
        # data_set = {"apple", "banana", "orange", "pear"}
        # self.browser_detailView.set_data(data_set)
        
        # create a button to add strings to the DetailListView
        add_button = QPushButton("Add Strings")
        add_button.clicked.connect(self.add_strings)
        
        # create a button to clear the contents of the DetailListView
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.browser_detailView.clear)
        
        # add the DetailListView and buttons to the layout
        layout.addWidget(self.browser_detailView)
        layout.addWidget(add_button)
        layout.addWidget(clear_button)
        self.x = 0
        self.show()
    
    def add_strings(self):
        # create a large list of unique strings
        if self.x == 0:
            string_list = ["apple", "banana", "orange", "kiwi"]
        else:
            string_list = ["apple", "banana", "ass", "kiwi"]

        
        # add the list of strings to the DetailListView
        self.browser_detailView.add_strings(string_list)
        self.x += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())