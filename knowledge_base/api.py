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
            (list of strings): names of entities related to given entity.
            e.g. ["Justin Timberlake", "Shawn Mendes"]
        """
        try:
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
                        # [("Justin Timberlake",), ("Shawn Mendes",)] => ["Justin Timberlake", "Shawn Mendes"]
                        return [x[0] for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not find entities similar to entity with name '{}': {}".format(entity_name, str(e)))
            return None

    def get_song_data(self, song_name):
        try:
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
        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve data for song with name '{}': {}".format(song_name, str(e)))
            return None

    def get_node_ids_by_entity_type(self, entity_name):
        """Retrieves and organizes IDs of all nodes that match given entity name.

        Return:
            (dict): key=entity_types of all nodes with the given name, val=list of int IDs. Empty if no matches.
                e.g. {"artist": [1, 2], "song": [5,7]}
        """
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT type, id
                            FROM nodes
                            WHERE name == (?)
                        """, (entity_name,))
                        node_ids_by_type = dict()
                        for x in cursor.fetchall():
                            ids = node_ids_by_type.setdefault(x[0], [])
                            ids.append(x[1])
                            node_ids_by_type[x[0]] = ids
                        return node_ids_by_type

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve ids for entity with name '{}': {}".format(entity_name, str(e)))
            return None

    def get_all_music_entities(self):
        """Gets a list of all the names, genres,
        artists, ect. in the DB

        :return: A list of all nouns in the database
        """
        try:
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
        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve music entities: {}".format(e))

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

    def _is_valid_entity_type(self, entity_type):
        """Indicates whether given entity type is valid.

        NOTE:
            - Ideally, we would have a table in our database for valid entity types.
            - Also, using enums would probably be cleaner.
        """
        return entity_type == "artist" or entity_type == "song"

    def add_artist(self, name):
        """Inserts given values into two tables: artists and nodes.

        Ensures that given artist is either added to both or neither of the songs and nodes tables.

        Returns:
            (bool): True if artist added to both songs and nodes table; False otherwise.
        """
        node_id = self._add_node(name, "artist")
        if node_id is None:
            print("ERROR: Failed to add artist '{}' to semantic network.".format(name))
            return False

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO artists (node_id) VALUES (?);
                        """, (node_id,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add artist '{0}'".format(
                name))
            return False

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add artist '{}' due to schema constraints: {}"
                .format(artist_name, str(e)))
            return False

        return True

    def add_song(self, name, artist):
        """Inserts given values into two tables: songs and nodes.

        Ensures that:
            - Given song is either added to both or neither of the songs and nodes tables.
            - Given artist is not ambiguous (only matches one 'artist' entry in nodes table).

        Returns:
            (bool): True if song added to both songs and nodes table; False otherwise.
        """
        matching_artist_node_ids = self.get_node_ids_by_entity_type(artist).get("artist", [])
        if len(matching_artist_node_ids) != 1:
            print("ERROR: Failed to add song '{}' because given artist '{}' corresponded to {} IDs (need 1)."
                .format(name, artist, len(matching_artist_node_ids)))
            return False
        artist_node_id = matching_artist_node_ids[0]

        node_id = self._add_node(name, "song")
        if node_id is None:
            print("ERROR: Failed to add song '{}' due to an error.".format(name))
            return False

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO songs (main_artist_id, node_id) VALUES (?, ?);
                        """, (artist_node_id, node_id,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add song '{}' with artist '{}'".format(
                name, artist))
            return False

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add song '{}' with artist '{}' due to schema constraints: {}"
                .format(name, artist, str(e)))
            return False

        return True

    def _add_node(self, entity_name, entity_type):
        """Adds given entity to knowledge representation system.

        In particular, this function adds a node to the semantic network by
        inserting it into the nodes table.

        Params:
            entity_name (string): for one of song, artist, etc.
                e.g. "Despacito", "Justin Bieber"

        Returns:
            id (int): id of new entry in nodes table for given entry; None if insertion failed.
        """
        if not self._is_valid_entity_type(entity_type):
            print("ERROR: Given entity type '{0}' is invalid.".format(entity_type))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        # NULL is passed so that SQLite assigns the auto-generated row_id value
                        # see:  - https://www.sqlite.org/autoinc.html
                        #       - https://stackoverflow.com/questions/7905859/is-there-an-auto-increment-in-sqlite
                        cursor.execute("""
                            INSERT INTO nodes (name, type, id) VALUES (?, ?, NULL);
                        """, (entity_name, entity_type,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not insert entity with name '{}' into nodes table: {}".format(entity_name, str(e)))
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Integrity constraints prevented insertion of entity with name '{}' into nodes table: {}"
                .format(entity_name, str(e)))
            return None

        node_ids = self.get_node_ids_by_entity_type(entity_name).get(entity_type, [])

        # NOTE: taking the max is a heuristic to disambiguate between multiplet matching ID:
        # Since we _just_ inserted the node and its id is autogenerated, it must have the largest id.
        return max(node_ids)
