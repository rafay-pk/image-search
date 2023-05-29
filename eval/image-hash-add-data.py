import sqlite3, os, imagehash, numpy as np
from PIL import Image
from difflib import SequenceMatcher


def list_files(folder):
    return [f"{root.replace(chr(92), '/')}/{f}" for root, _, file in os.walk(folder) for f in file]


conn = sqlite3.connect(r'C:\Users\Rafay\repos\image-search\data\database.db')
cursor = conn.cursor()


def add_data(folder_path):
    extensions = {'.png', '.jpg'}

    for file in list_files(folder_path):
        if any([file.endswith(ext) for ext in extensions]):
            path = os.path.join(folder_path, file)
            img_hash = imagehash.phash(Image.open(path))
            print(f'{path}:{img_hash}')
            cursor.execute('INSERT OR IGNORE INTO Files (path, hash) VALUES (?, ?)', (path, str(img_hash)))

    conn.commit()

    cursor.execute('SELECT f.id, f.hash FROM Files f;')
    data = np.array(cursor.fetchall())
    similar = []

    for i in range(len(data) - 1):
        # if score > 0.7:
        if SequenceMatcher(None, data[i][1], data[i + 1][1]).ratio() > 0.7:
            cursor.execute(f'SELECT f.path FROM Files f WHERE f.id = {data[i][0]}')
            path1 = cursor.fetchone()
            cursor.execute(f'SELECT f.path FROM Files f WHERE f.id = {data[i + 1][0]}')
            path2 = cursor.fetchone()
            similar.append([path1, path2])

    [print(x, sep='\n') for x in similar]
    print('merging')

    deleted = 0
    for i in range(len(similar) - 1):
        i = i - deleted
        curr_list = set(similar[i])
        next_list = set(similar[i + 1])
        if curr_list.intersection(next_list):
            similar[i] = list(curr_list.union(next_list))
            del similar[i + 1]
            deleted += 1

    [print(x, sep='\n') for x in similar]

    cursor.execute('DROP TABLE IF EXISTS Collections;')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER,
            file_id INTEGER
        );
    ''')

    collection_counter = 0

    for collection in similar:
        collection_counter += 1
        for file in collection:
            cursor.execute('SELECT f.id FROM Files f WHERE f.path = ?', (file))
            file_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO Collections (collection_id, file_id) VALUES (?, ?)', (collection_counter, file_id))

    conn.commit()


add_data('C:/Users/Rafay/OneDrive/Pictures')
