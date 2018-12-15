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
        self.approved_relations = dict(
            similarity="similar to",
            genre="of genre",
        )

    def __str__(self):
        return "Knowledge Representation API object for {} DB.".format(self.dbName)

    @property
    def connection(self):
        conn = sqlite3.connect(self.dbName)
        # enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = 1")
        return conn

    def get_related_entities(self, entity_name, rel_str="similar to"):
        """Finds all entities connected to the given entity in the semantic network.

        The given entity may be any of song, an artist, etc. The returned entity may or may not be
        the same type of entity.

        A warning is issued if the given rel_str not one of the 'approved' ones.

        Params:
            entity_name (string): name of entity (e.g. "Justin Bieber").
            rel_str (string): e.g. "similar to", "of genre".

        Returns:
            (list of strings): names of entities related to given entity.
            e.g. ["Justin Timberlake", "Shawn Mendes"]
        """
        if rel_str not in self.approved_relations.values():
            print("WARN: querying for invalid relations. Only allow: {}".format(self.approved_relations))

        try:
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    with closing(con.cursor()) as cursor:
                        # Inner query retrieves IDs of all related entities
                        cursor.execute("""
                            SELECT name
                            FROM nodes
                            WHERE id IN (
                                SELECT dest
                                FROM edges JOIN nodes ON source == id
                                WHERE name = (?) AND rel == (?)
                            );
                        """, (entity_name, rel_str))
                        # [("Justin Timberlake",), ("Shawn Mendes",)] => ["Justin Timberlake", "Shawn Mendes"]
                        return [x[0] for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not find entities similar to entity with name '{}': {}".format(entity_name, str(e)))
            return []

    def get_song_data(self, song_name):
        """Gets all songs that match given name, along with their artists.

        Returns:
            (list of dicts): each dict contains song_name and artist_name keys. Empty if not matches found.
                e.g. [
                    {
                        id: 1,
                        song_name: "Despacito",
                        artist_name: "Justin Bieber",
                        duration_ms: 11111,
                        popularity: 100,
                    },
                    ...
                ]
        """
        try:
            # Auto-close.
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close.
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT song.name, artist.name, song.duration_ms, song.popularity, song_id
                            FROM (
                                SELECT name, main_artist_id, duration_ms, popularity, id as song_id
                                FROM songs JOIN nodes ON node_id == id
                                WHERE name == (?)
                            ) AS song JOIN nodes AS artist ON main_artist_id == id;
                        """, (song_name,))
                        return [
                            dict(
                                song_name=x[0],
                                artist_name=x[1],
                                duration_ms=x[2],
                                popularity=x[3],
                                id=x[4],
                            ) for x in cursor.fetchall()
                        ]

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve data for song with name '{}': {}".format(song_name, str(e)))
            return []

    def get_artist_data(self, artist_name):
        """Get artist info.

        Params:
            artist_name (string): e.g. "Justin Bieber".

        Returns:
            (list of dict): keys: id, name, num_spotify_followers, genres. Empty if no matching artists found.
                e.g. [{
                    genres=['Pop'],
                    id=1,
                    num_spotify_followers=4000,
                    name="Justin Bieber",
                }, ...]
        """
        try:
            # Auto-close.
            with closing(self.connection) as con:
                # Auto-commit
                with con:
                    # Auto-close.
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT id, name, num_spotify_followers
                            FROM artists JOIN nodes ON node_id == id
                            WHERE name == (?);
                        """, (artist_name,))
                        res_tuples = cursor.fetchall()

        except sqlite3.OperationalError as e:
            print("ERROR: Could not retrieve data for artist with name '{}': {}".format(artist_name, str(e)))
            return []

        results = []
        for res_tuple in res_tuples:
            results.append(dict(
                id=res_tuple[0],
                name=res_tuple[1],
                num_spotify_followers=res_tuple[2],
                genres=self.get_related_entities(artist_name, self.approved_relations["genre"]),
            ))
        return results

    def get_songs_by_artist(self, artist):
        """Retrieves list of songs for given artist.

        Param:
            artist (string): e.g. "Justin Bieber"

        Returns:
            (list of strings): song names by given artist. None if artist is ambiguous or not found.
                e.g. ["Despacito", "Sorry"]
        """
        matching_artist_node_ids = self._get_matching_node_ids(artist)
        if len(matching_artist_node_ids) == 0:
            print("ERROR: could not find entry for artist '{}'".format(artist))
            return None

        elif len(matching_artist_node_ids) > 1:
            print("ERROR: found multiple entries for ambiguous artist name '{}'.".format(artist))
            return None

        artist_node_id = matching_artist_node_ids[0]
        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            SELECT name
                            FROM (
                                SELECT songs.node_id as node_id
                                FROM songs JOIN artists ON main_artist_id = artists.node_id
                                WHERE artists.node_id = (?)
                            ) as x JOIN nodes ON x.node_id = id;
                        """, (artist_node_id,))

                        # unpack tuples e.g. [("Despacito",)] => ["Despacito"]
                        return [x[0] for x in cursor.fetchall()]

        except sqlite3.OperationalError as e:
            print("ERROR: failed to find songs for artist '{0}'".format(
                artist))
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
            return []

    def _get_matching_node_ids(self, node_name):
        """Retrieves IDs of all nodes matching the given name.

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
                E.g. "similar to", "of genre".

            score (int): edge weight corresponding to percentage, must be [0,100] range.

        Returns:
            (bool): False if error occurred, True otherwise.
        """
        if rel_str not in self.approved_relations.values():
            print("WARN: adding unapproved relation. Only allow: {}".format(self.approved_relations))

        matching_src_nodes = self._get_matching_node_ids(source_node_name)
        matching_dst_nodes = self._get_matching_node_ids(dest_node_name)
        if len(matching_src_nodes) != 1 or len(matching_dst_nodes) != 1:
            print("ERROR: Could not find unique match for entities '{}', '{}'. Found {}, {} matches respectively" .format(
                source_node_name,
                dest_node_name,
                len(matching_src_nodes),
                len(matching_dst_nodes)),
            )
            return False

        source_node_id, dest_node_id = matching_src_nodes[0], matching_dst_nodes[0]

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
        return entity_type in ["artist", "song", "genre"]

    def add_artist(self, name, genres=[], num_spotify_followers=None):
        """Inserts given values into two tables: artists and nodes.

        Ensures that:
        - Given artist is only added if they are not already in the database.
        - Given artist is either added to both or neither.

        Params:
            name (string): e.g. "Justin Bieber"
            genres (list): e.g. ['indie r&b', 'malaysian indie']
            num_spotify_followers (int): number of Spotify followers.

        Returns:
            (int): node_id corresponding to given artist if added or already existed; None otherwise.
        """
        matching_nodes = self.get_node_ids_by_entity_type(name).get("artist", [])
        if len(matching_nodes) > 0:
            print("WARN: Artist '{}' already exists in semantic network. Aborting insertion.".format(name))
            return matching_nodes[0]

        node_id = self._add_node(name, "artist")
        if node_id is None:
            print("ERROR: Failed to add artist '{}' to semantic network.".format(name))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO artists (node_id, num_spotify_followers) VALUES (?, ?);
                        """, (node_id, num_spotify_followers))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add artist '{0}'".format(
                name))
            return node_id

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add artist '{}' due to schema constraints: {}"
                .format(name, str(e)))
            return node_id

        for genre in genres:
            if self.add_genre(genre) is not None:
                genre_rel_str = self.approved_relations["genre"]
                if not self.connect_entities(name, genre, genre_rel_str, 100):
                    print("ERROR: could not connect genre '{}' and artist '{}'".format(genre, name))

            else:
                print("ERROR: Could not add genre '{}' for artist '{}'".format(genre, name))

        return node_id

    def add_song(self, name, artist, duration_ms=None, popularity=None):
        """Inserts given values into two tables: songs and nodes.

        Ensures that:
            - Given song is either added to both or neither.
            - Given artist is not ambiguous (only matches one 'artist' entry in nodes table).
            - Given tuple (song, artist) is only added if it does not already exist in database.

        Params:
            name (string): e.g. "Despacito"
            artist (string): e.g. "Justin Bieber"
            duration_ms (int): length of song e.g. 22222.
            popularity (int): in [0,100] range.

        Returns:
            (int): node_id corresponding to song if added or already existed; None otherwise.
        """
        matching_artist_node_ids = self.get_node_ids_by_entity_type(artist).get("artist", [])
        if len(matching_artist_node_ids) != 1:
            print("ERROR: Failed to add song '{}' because given artist '{}' corresponded to {} IDs (need 1)."
                .format(name, artist, len(matching_artist_node_ids)))
            return None
        artist_node_id = matching_artist_node_ids[0]

        existing_songs = self.get_song_data(name)
        for tmp_song in existing_songs:
            if tmp_song["artist_name"] == artist:
                print("WARN: Song '{}' by artist '{}' already exists in semantic network. Aborting insertion.".format(name, artist))
                return None

        node_id = self._add_node(name, "song")
        if node_id is None:
            print("ERROR: Failed to add song '{}' due to an error.".format(name))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO songs (main_artist_id, node_id, duration_ms, popularity)
                            VALUES (?, ?, ?, ?);
                        """, (artist_node_id, node_id, duration_ms, popularity))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add song '{}' with artist '{}'".format(
                name, artist))
            return node_id

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add song '{}' with artist '{}' due to schema constraints: {}"
                .format(name, artist, str(e)))
            return node_id

        return node_id

    def add_genre(self, name):
        """Adds given value into two tables: genres and nodes.

        Ensures that:
        - Given genre is eiter added to both or neither.
        - Given genre is only added if not already in the database.

        Returns:
            (int): node_id if genre was added or it already existed; None otherwise (e.g. error occurred).
        """
        matching_nodes = self.get_node_ids_by_entity_type(name).get("genre", [])
        if len(matching_nodes) > 0:
            print("WARN: Genre '{}' already exists in semantic network. Aborting insertion.".format(name))
            return matching_nodes[0]

        node_id = self._add_node(name, "genre")
        if node_id is None:
            print("ERROR: Failed to add genre '{}' to semantic network.".format(name))
            return None

        try:
            with closing(self.connection) as con:
                with con:
                    with closing(con.cursor()) as cursor:
                        cursor.execute("""
                            INSERT INTO genres (node_id) VALUES (?);
                        """, (node_id,))

        except sqlite3.OperationalError as e:
            print("ERROR: Could not add artist '{0}'".format(
                name))
            return None

        except sqlite3.IntegrityError as e:
            print("ERROR: Could not add genre '{}' due to schema constraints: {}"
                .format(name, str(e)))
            return None
        return node_id

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
