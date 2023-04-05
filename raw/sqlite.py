import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up database connection
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("example.db")
        if not db.open():
            print("Error opening database")
            sys.exit(1)

        # Create a table in the database
        query = QSqlQuery()
        query.exec(
            "CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY, name TEXT)")

        # Populate the table with some data
        query.prepare("INSERT INTO my_table (name) VALUES (:name)")
        query.bindValue(":name", "John")
        query.exec()
        query.bindValue(":name", "Jane")
        query.exec()

        # Set up model and view to display the table
        model = QSqlTableModel()
        model.setTable("my_table")
        model.select()
        view = QTableView()
        view.setModel(model)

        # Add the view to the main window
        self.setCentralWidget(view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
