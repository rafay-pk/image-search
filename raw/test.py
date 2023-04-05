from PyQt6.QtWidgets import QApplication, QWidget, QToolBar
from PyQt6.QtGui import QAction

app = QApplication([])
window = QWidget()

# create toolbar and add actions
toolbar = QToolBar()
action1 = QAction("Action 1", window)
action2 = QAction("Action 2", window)
toolbar.addAction(action1)
toolbar.addAction(action2)

# add toolbar to the widget
window.addToolBar(toolbar)

window.show()
app.exec()