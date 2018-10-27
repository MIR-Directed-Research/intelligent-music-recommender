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
        conn = sqlite3.connect(self.dbName)
        # enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = 1")
        return conn

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
                        WHERE id IN (
                            SELECT dest
                            FROM edges JOIN nodes ON source == id
                            WHERE name = (?) AND rel == "similar to"
                        );
                    """, (entity_name,))
                    return [x[0] for x in cursor.fetchall()]
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
                        FROM songs JOIN nodes ON node_id == id
                        WHERE name == (?)
                    ) AS song JOIN nodes AS artist ON main_artist_id == id;
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
                        SELECT name AS song_name
                        FROM songs JOIN nodes ON node_id == id
                        UNION
                        SELECT name AS artist_name
                        FROM artists JOIN nodes ON node_id == id
                        """)
                    return [x[0] for x in cursor.fetchall()]

    def _get_matching_node_ids(self, node_name):
        """Retrieves IDs of all node matching the given name.

        Params:
            node_name (string): name of entity node. E.g. "Justin Bieber".

        Returns:
            (list of ints): ids of nodes corresponding to given name; empty if none found.
        """
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT id
                            FROM nodes
                            WHERE name == (?)
                        """, (node_name,))
                        res = cursor.fetchall()

        except sqlite3.OperationalError as e:
            print("ERROR: An error occurred when retrieving node ids: {}".format(e))

        if len(res) == 0:
            print("ERROR: Could not find node ID for name '{0}'.".format(node_name))
            return []

        elif len(res) > 1:
            print("Found multiple node IDs for name '{0}', returning first result.".format(node_name))

        # e.g. [(10,), (11,)] => [10, 11]
        return [x[0] for x in res]

    def connect_entities(self, source_node_name, dest_node_name, rel_str, score):
        """Inserts edge row into edges table.

        Params:
            source_node_name (string): Node name of entity with the outgoing edge.
                E.g. "Justin Bieber"; "Despacito"; "Pop"; etc.

            dest_node_name (string): Node name of entity with the incoming edge.
                E.g. "Shawn Mendes"; "In My Blood"; "Pop"; etc.

            rel_str (string): Type of relationship, which must be already present in 'relations' table.
                E.g. "similar to".

            score (int): edge weight corresponding to percentage, must be [0,100] range.

        Returns:
            (bool): False if error occurred, True otherwise.
        """
        candidate_source_ids = self._get_matching_node_ids(source_node_name)
        candidate_dest_ids = self._get_matching_node_ids(dest_node_name)
        if len(candidate_source_ids) != 1 or len(candidate_dest_ids) != 1:
            print("ERROR: Could not find unique match for entities '{}', '{}'. Found {}, {} matches respectively" .format(
                source_node_name,
                dest_node_name,
                len(candidate_source_ids),
                len(candidate_dest_ids)),
            )
            return False

        source_node_id, dest_node_id = candidate_source_ids[0], candidate_dest_ids[0]

        try:
            with closing(self.connection) as conn:
                with conn:
                    with closing(conn.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO edges (source, dest, rel, score)
                            VALUES (?, ?, ?, ?)
                        """, (source_node_id, dest_node_id, rel_str, score))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not connect entities '{0}' and '{1}': {2}".format(
                source_node_name, dest_node_name, str(e)))
            return False

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not connect entities '{0}' and '{1}' due to schema constraints: {2}".format(
                source_node_name, dest_node_name, str(e)))
            return False

        return True
