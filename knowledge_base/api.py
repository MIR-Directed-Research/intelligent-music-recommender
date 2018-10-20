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
                    SELECT song.name, artist.name
                    FROM (
                        SELECT name, main_artist_id
                        FROM songs JOIN nodes on node_id == id
                        WHERE name == (?)
                    ) AS song JOIN nodes AS artist on main_artist_id == id;
                    """, (song_name,))
                    return cursor.fetchone()

    def get_all_music_entities(self):
        """Gets a list of all the names, genres,
        artists, ect. in the DB

        :return: A list of all nouns in the database
        """
        # Auto-close.
        with closing(self.connection) as con:
            # Auto-commit
            with con:
                # Auto-close.
                with closing(con.cursor()) as cursor:
                    cursor.execute("""
                        SELECT name
                        FROM songs
                        UNION
                        SELECT name
                        FROM artists
                        """)
                    return cursor.fetchone()
