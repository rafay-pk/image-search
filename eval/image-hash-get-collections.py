import sqlite3

conn = sqlite3.connect(r'C:\Users\Rafay\repos\image-search\data\database.db')
cursor = conn.cursor()

cursor.execute('SELECT c.collection_id, c.file FROM Collections c')
result = cursor.fetchall()

# [print(x, sep='\n') for x in result]