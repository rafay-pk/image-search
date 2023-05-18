import sqlite3
import threading

# Create a new SQLite database file
conn = sqlite3.connect('example2.db', check_same_thread=False)

# Create a table for storing data
conn.execute('''CREATE TABLE IF NOT EXISTS test_table
             (id INTEGER PRIMARY KEY, value TEXT)''')

# Define a function for inserting data into the database
def insert_data(value):
    conn.execute("INSERT INTO test_table (value) VALUES (?)", (value,))
    conn.commit()

# Define a function for reading data from the database
def read_data():
    cursor = conn.execute("SELECT * FROM test_table")
    for row in cursor:
        print(row)

# Define a function that will repeatedly insert data into the database
def insert_loop():
  for i in range(2):
    insert_data('some data')

# Define a function that will repeatedly read data from the database
def read_loop():
  for i in range(2):
    read_data()

# Start two threads for inserting and reading data
insert_thread = threading.Thread(target=insert_loop)
read_thread = threading.Thread(target=read_loop)
insert_thread.start()
read_thread.start()
