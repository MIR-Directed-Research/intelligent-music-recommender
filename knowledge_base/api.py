import sqlite3

class KnowledgeBaseAPI:
    """
    This layer stores the interface to the knowledge-engine.
    It is primarily used by the query-engine and knowledge-generation
    components.
    """

    def __init__(self, dbName):
        self.dbName = dbName
        self.conn = None

    def open_connection(self):
        """
        Returns:
            (bool): indicates success.
        """
        try:
            self.conn = sqlite3.connect(self.dbName)
        except sqlite3.Error as e:
            print(f"ERR: Failed to open connection to db: '{self.dbName}'")
            return False
        return True

    def get_song_data(self, song_name):
        if self.conn is None:
            return None

        get_song_sql = f"""
            SELECT *
            FROM songs
            WHERE name == "{song_name}";
        """
        try:
            cursor = self.conn.cursor()
        except sqlite3.ProgrammingError as e:
            print(f"ERR: Must open connection to DB before executing query.")
            return None

        try:
            cursor.execute(get_song_sql)
            self.conn.commit()
            res = cursor.fetchone()

        except sqlite3.Error as e:
            print(f"{e}: An error occurred when querying for song: {song_name}")
            res = None

        finally:
            cursor.close()

        return res

    def close_connection(self):
        if self.conn is None:
            return
        self.conn.close()

    def __str__(self):
        return f"Knowledge Representation API object for {self.dbName} DB."

    # TODO: Implement.
    @staticmethod
    def get_all_nouns():
        """Gets a list of all the names, genres,
        artists, ect. in the DB

        :return: A list of all nouns in the database
        """
        return ['example']
