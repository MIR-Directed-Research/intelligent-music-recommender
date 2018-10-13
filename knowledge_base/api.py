import sqlite3
from contextlib import closing


class KnowledgeBaseAPI:
    """
    This layer stores the interface to the knowledge-engine.
    It is primarily used by the query-engine and knowledge-generation
    components.
    """

    def __init__(self, dbName):
        self.dbName = dbName

    def __str__(self):
        return "Knowledge Representation API object for {} DB.".format(self.dbName)

    @property
    def connection(self):
        return sqlite3.connect(self.dbName)

    def get_song_data(self, song_name):
        # Auto-close.
        with closing(self.connection) as con:
            # Auto-commit
            with con:
                # Auto-close.
                with closing(con.cursor()) as cursor:
                    cursor.execute("""
                    SELECT *
                    FROM songs
                    WHERE name == (?);
                    """, (song_name,))
                    return cursor.fetchone()

    @staticmethod
    def get_all_nouns():
        """Gets a list of all the names, genres,
        artists, ect. in the DB

        :return: A list of all nouns in the database
        """
        return ['example']
