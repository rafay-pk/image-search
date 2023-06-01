from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListView,
    QListWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

class QDeselectableListWidget(QListWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QListWidget.mousePressEvent(self, event)


class QDeselectableTreeView(QTreeView):
    def mousePressEvent(self, event):
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)
        # self.other_func()


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