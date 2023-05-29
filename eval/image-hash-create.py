import sqlite3

# Create a connection to the database
conn = sqlite3.connect(r'C:\Users\Rafay\repos\image-search\data\database.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS Files;')
# Create the table to store image data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        hash TEXT NOT NULL
    );
''')
cursor.execute('create index idx_hash on Files(hash asc);')