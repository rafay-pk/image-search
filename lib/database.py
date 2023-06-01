import sqlite3, os, base64, numpy as np

class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect('data/database.sqlite', check_same_thread=False)
        self.__execute_query_from_file('sql/create.sql')

    def __execute_query_from_file(self, file_path):
        if not os.path.isfile(file_path):
            raise ValueError("File path is not valid.")
        with open(file_path, "r") as f:
            queries = f.read().split(";")
            for query in queries:
                query = query.strip()
                if query:
                    self.__execute_query(query)

    def __execute_query(self, query):
        self.conn.execute(query)
        self.conn.commit()

    def __fetch_data(self, query):
        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def get_all_folders(self):
        return [x[0] for x in self.__fetch_data(f"SELECT f.org_path FROM Folders f")]

    def get_files_in_folder(self, sym_path):
        return self.__fetch_data(f"SELECT f.org_path FROM Folders f WHERE sym_path = '{sym_path}'")[0][0]

    def get_all_files(self):
        return [x[0] for x in self.__fetch_data("SELECT f.path FROM Files f")]
    
    def get_all_folders(self):
        return [x[0] for x in self.__fetch_data(f"SELECT f.org_path FROM Folders f")]
    
    def get_all_captions(self):
        return [x[0] for x in self.__fetch_data(f"SELECT caption FROM Files")]

    def get_caption(self, path):
        return self.__fetch_data(f"SELECT f.caption FROM Files f WHERE f.path = '{path}'")[0][0]
    
    def get_file_from_caption(self, caption):
        return self.__fetch_data(f"SELECT f.path FROM Files f WHERE f.caption = '{caption}'")[0][0]

    def add_new_tag(self, tag):
        self.__execute_query(f"INSERT OR IGNORE INTO Tags (name) VALUES ('{tag}')")

    def edit_tag(self, tag, new_tag):
        self.__execute_query(f"UPDATE Tags SET name = '{new_tag}' WHERE name = '{tag}'")
        self.__execute_query(f"UPDATE People SET name = '{new_tag}' WHERE name = '{tag}'")

    def delete_tag(self, tag):
        self.__execute_query(f"DELETE FROM Tags WHERE name = '{tag}'")
        # Select id of that tag and then remove all filetags with that id

    def add_folder(self, folder, sym_path):
        self.__execute_query(f"INSERT INTO Folders (org_path, sym_path) VALUES ('{folder}', '{sym_path}')")

    def add_files(self, files):
        for file in files:
            self.__execute_query(f"INSERT INTO Files (path) VALUES ('{file}')")

    def delete_files(self, files):
        for file in files:
            self.__execute_query(f"DELETE FROM Files WHERE path = '{file}'")

    def add_tag_to_file(self, tag, file):
        self.add_new_tag(tag)
        query = f"""INSERT OR IGNORE INTO FileTags (file_id, tag_id) VALUES 
                    (
                        (SELECT id FROM Files WHERE path = '{file}'),
                        (SELECT id FROM Tags WHERE name = '{tag}')
                    );"""
        self.__execute_query(query)

    def add_caption_to_file(self, caption, file):
        self.__execute_query('UPDATE Files SET caption = "' + caption + f'" WHERE path = "{file}"')

    def remove_tag_from_file(self, tag, file):
        query = f"""DELETE FROM FileTags WHERE file_id = (SELECT id FROM Files WHERE path = '{file}')
                    AND tag_id = (SELECT id FROM Tags WHERE name = '{tag}')"""
        self.__execute_query(query)

    def get_all_files(self):
        return [x[0] for x in self.__fetch_data("SELECT f.path FROM Files f")]

    def get_files_in_folder(self, sym_path):
        return self.__fetch_data(f"SELECT f.org_path FROM Folders f WHERE sym_path = '{sym_path}'")[0][0]

    def get_file_tags(self, file):
        query = f"""SELECT t.name FROM FileTags ft
                        JOIN Files f
                            ON ft.file_id = f.id 
                        JOIN Tags t 
                            ON ft.tag_id = t.id 
                        WHERE f.path = '{file}'"""
        return [x[0] for x in self.__fetch_data(query)]

    def check_tag_exists(self, file, tag):
        tags = self.__fetch_data(
            f"SELECT t.name FROM Tags t JOIN FileTags ft ON  t.id = ft.tag_id JOIN Files f ON ft.file_id = f.id WHERE f.path = '{file}'")
        return tag in [x[0] for x in tags]

    def search_inclusive(self, tags):
        query = f"""SELECT DISTINCT f.path FROM Files f
                        JOIN FileTags ft
                            ON f.id = ft.file_id
                        JOIN Tags t
                            ON ft.tag_id = t.id
                        WHERE t.name = '{tags[0]}'"""
        for tag in tags[1:]:
            query += f" OR t.name = '{tag}'"
        return [x[0] for x in self.__fetch_data(query)]

    def add_face_encoding(self, name, encoding):
        enc = base64.binascii.b2a_base64(encoding).decode("ascii")
        self.__execute_query(f"INSERT OR IGNORE INTO People (name, encoding) VALUES ('{name}', '{enc}')")

    def get_all_encodings(self):
        return [np.frombuffer(base64.binascii.a2b_base64(x[0].encode("ascii"))) for x in
                self.__fetch_data("SELECT encoding FROM People")]

    def get_person_name(self, encoding):
        enc = base64.binascii.b2a_base64(encoding).decode("ascii")
        return self.__fetch_data(f"SELECT name FROM People WHERE encoding = '{enc}'")[0][0]

    def get_all_people(self):
        return [x[0] for x in self.__fetch_data("SELECT name FROM People")]
