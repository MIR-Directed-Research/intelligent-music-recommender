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

    def get_similar_entities(self, entity_name):
        """ Finds all entities similar to a given entity.

        An entity may be a song, an artist, etc.

        Params:
            entity_name (string): name of entity (e.g. "Justin Bieber").
        Returns:
            (list of 1-tuples): names of entities related to given entity.
            e.g. [("Justin Timberlake",), ("Shawn Mendes",)]
        """
        with closing(self.connection) as con:
            # Auto-commit
            with con:
                with closing(con.cursor()) as cursor:
                    # Inner query retrieves IDs of all similar entities
                    cursor.execute("""
                        SELECT name
                        FROM nodes
                        WHERE id in (
                            SELECT dest
                            FROM edges join nodes on source == id
                            WHERE name = (?) AND rel == "similar to"
                        );
                    """, (entity_name,))
                    return cursor.fetchall()
        return None


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
