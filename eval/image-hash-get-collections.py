import sqlite3

conn = sqlite3.connect('image_data.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM Collections')
print(cursor.fetchall())