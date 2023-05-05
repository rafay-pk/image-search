from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar
from PyQt6.QtGui import QAction, QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create two QAction objects for the toggle buttons
        self.action1 = QAction("Button 1", self, checkable=True)
        self.action2 = QAction("Button 2", self, checkable=True)

        # Set one of the actions to be checked initially
        self.action1.setChecked(True)

        # Connect the toggled signal of the actions to their respective functions
        self.action1.toggled.connect(lambda checked: self.button_clicked(self.action1, self.action2, checked))
        self.action2.toggled.connect(lambda checked: self.button_clicked(self.action2, self.action1, checked))

        # Add the actions to a toolbar
        toolbar = QToolBar()
        toolbar.addAction(self.action1)
        toolbar.addAction(self.action2)
        self.addToolBar(toolbar)

    def button_clicked(self, clicked_action, other_action, checked):
        if checked:
            other_action.trigger()
        else:
            # If both actions are unchecked, set the state of one of them to checked again
            if not self.action1.isChecked() and not self.action2.isChecked():
                clicked_action.setChecked(True)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
