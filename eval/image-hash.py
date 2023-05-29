import imagehash, os
from PIL import Image

folder_path = 'C:/Users/Rafay/OneDrive/Pictures'
extensions = {'.png', '.jpg'}
table = {}

for file in os.listdir(folder_path):
    if any([file.endswith(ext) for ext in extensions]):
        path = os.path.join(folder_path, file)
        table[path] = imagehash.phash(Image.open(path))

table = dict(sorted(table.items(), key=lambda x: str(x[1])))
paths = list(table.keys())
hashes = list(table.values())
similar = []

for i in range(len(hashes) - 1):
    diff = hashes[i + 1] - hashes[i]
    if diff < 5:
        similar.append([paths[i], paths[i + 1]])

[print(x, sep='\n') for x in similar]

deleted = 0
for i in range(len(similar) - 1):
    i = i - deleted
    curr_list = set(similar[i])
    next_list = set(similar[i + 1])
    if curr_list.intersection(next_list):
        similar[i] = list(curr_list.union(next_list))
        del similar[i + 1]
        deleted += 1

print('\nLists Merged\n')
[print(x, sep='\n') for x in similar]

# import imagehash
# import os
# from PIL import Image
# import sqlite3
#
#
# def file_op(f):
#     return f.replace('\\', '/')
#
# # Create a connection to the database
# conn = sqlite3.connect('image_data.db')
# cursor = conn.cursor()
# cursor.execute('DROP TABLE IF EXISTS images;')
# # Create the table to store image data
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS images (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         path TEXT,
#         hash INTEGER
#     );
# ''')
# cursor.execute('create index idx_hash on images(hash asc);')
# # Folder path and extensions
# folder_path = 'C:/Users/Rafay/OneDrive/Pictures'
# extensions = {'.png', '.jpg'}
# count = 0
# # Populate the table with image data
# for file in [f'{file_op(root)}/{f}' for root, dir, file in os.walk(folder_path) for f in file]:
#     if any([file.endswith(ext) for ext in extensions]):
#         path = os.path.join(folder_path, file)
#         img = Image.open(path)
#         count += 1
#         img_hash = imagehash.phash(img, hash_size=16)
#
#         # Insert image data into the table
#         cursor.execute('INSERT INTO images (path, hash) VALUES (?, ?)', (path, str(img_hash)))
#
# # Commit the changes to the database
# conn.commit()
#
# # Retrieve similar images using SQL queries
# cursor.execute('''
#     SELECT a.path, b.path
#     FROM images a
#     JOIN images b ON a.hash - b.hash = 0
#     WHERE a.id = b.id + 1
# ''')
# similar = cursor.fetchall()
#
# # Print the similar image pairs
# # for pair in similar:
# #     print(pair)
#
# # Merge similar image lists
# deleted = 0
# for i in range(len(similar) - 1):
#     i = i - deleted
#     curr_list = set(similar[i])
#     next_list = set(similar[i + 1])
#     if curr_list.intersection(next_list):
#         similar[i] = list(curr_list.union(next_list))
#         del similar[i + 1]
#         deleted += 1
#
# print('\nLists Merged\n')
# for lst in similar:
#     print(lst)
#
# # Close the database connection
# conn.close()
#
#
# print(f'OriginalFiles={count}, Classified={sum(len(sublist) for sublist in similar)}')