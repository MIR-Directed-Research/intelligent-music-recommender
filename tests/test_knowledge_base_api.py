import unittest

import os

from knowledge_base.api import KnowledgeBaseAPI


class TestMusicKnowledgeBaseAPI(unittest.TestCase):

    def setUp(self):
        # TODO: ensure test.db exists?
        DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            DB_path = "test.db"
        self.kb_api = KnowledgeBaseAPI(dbName=DB_path)

    def test_get_song_data(self):
        res = self.kb_api.get_song_data("Despacito")
        # we don't care what the node ID is
        self.assertEqual(
            res, ('Despacito', 'Justin Bieber'),
            "Queried song data did not match expected.",
        )

    def test_get_song_data_dne(self):
        res = self.kb_api.get_song_data("Not In Database")
        self.assertEqual(res, None, "Expected 'None' result for queried song not in DB.")

    def test_find_similar_song(self):
        res = self.kb_api.get_similar_entities("Despacito")
        self.assertEqual(
            len(res), 1,
            "Expected only one song similar to \"Despacito\". Found {0}".format(res),
        )
        self.assertEqual(
            res[0], "Rock Your Body",
            "Expected to find \"Rock Your Body\" as similar to \"Despacito\".",
        )

    def test_find_similar_artist(self):
        res = self.kb_api.get_similar_entities("Justin Bieber")
        self.assertEqual(
            len(res), 2,
            "Expected exactly two artists similar to Justin Bieber.",
        )
        self.assertEqual(
            res[0], "Justin Timberlake",
            "Expected to find Justin Timberlake as similar to Justin Bieber.",
        )
        self.assertEqual(
            res[1], "Shawn Mendes",
            "Expected to find Justin Timberlake as similar to Justin Bieber.",
        )

    def test_get_all_music_entities(self):
        res = self.kb_api.get_all_music_entities()
        self.assertTrue(
            'Justin Bieber' in res,
            'Expected to find "Justin Bieber" in the list of entities.'
        )

    def test_find_similar_to_entity_that_dne(self):
        res = self.kb_api.get_similar_entities("Unknown Entity")
        self.assertEqual(res, [])

    def test_connect_entities(self):
        res = self.kb_api.get_similar_entities("Shawn Mendes")
        self.assertEqual(len(res), 0)

        res = self.kb_api.connect_entities("Shawn Mendes", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, True, "")

        res = self.kb_api.get_similar_entities("Shawn Mendes")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "Justin Timberlake")

    def test_rejects_connect_ambiguous_entities(self):
        res = self.kb_api.add_artist("Artist and Song name clash")
        res = self.kb_api.add_song("Artist and Song name clash", "U2")

        res = self.kb_api.connect_entities("Artist and Song name clash", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, False, "")

    def test_add_artist(self):
        res = self.kb_api.add_artist("Heart")
        self.assertEqual(res, True, "Failed to add artist 'Heart' to knowledge base.")

        res = self.kb_api.get_node_ids_by_entity_type("Heart")
        self.assertTrue("artist" in res,
            "Expected to find an 'artist' entity with name 'Heart', but got: {0}".format(res))

    def test_add_song(self):
        res = self.kb_api.add_song("Heart", "Justin Bieber")
        self.assertEqual(res, True, "Failed to add song 'Heart' by artist 'Justin Bieber' to knowledge base.")

        res = self.kb_api.get_node_ids_by_entity_type("Heart")
        self.assertTrue("song" in res,
            "Expected to find an 'song' entity with name 'Heart', but got: {0}".format(res))

    # The logic tested here is currently implemented in the KR API
    # However, if it is moved to the schema (e.g. trigger functions),
    # then this test can be moved to the schema test module
    def test_new_song_with_unknown_artist_rejected(self):
        res = self.kb_api.add_song("Song by Unknown Artist", "Unknown artist")
        self.assertEqual(res, False, "Expected song with unknown artist to be rejected")

        res = self.kb_api.get_node_ids_by_entity_type("Song by Unknown Artist")
        self.assertTrue("song" not in res,
            "Insertion of song with unknown artist should not have been added to nodes table")

    def test_contains_entity(self):
        res = self.kb_api.get_node_ids_by_entity_type("Justin Timberlake")
        self.assertTrue("artist" in res,
            "Expected to find an 'artist' entity with name 'Justin Timberlake', but got: {0}".format(res))
        self.assertEqual(len(res["artist"]), 1,
            "Expected to find exactly one entity (of type 'artist') with name 'Justin Timberlake', but got: {0}".format(res))

        res = self.kb_api.get_node_ids_by_entity_type("Despacito")
        self.assertTrue("song" in res,
            "Expected to find an 'song' entity with name 'Despacito', but got: {0}".format(res))
        self.assertEqual(len(res["song"]), 1,
            "Expected to find exactly one entity (of type 'song') with name 'Despacito', but got: {0}".format(res))

        res = self.kb_api.get_node_ids_by_entity_type("Unknown entity")
        self.assertEqual(res, {}, "Expected no results from query for unknown entity, but got {}".format(res))


if __name__ == '__main__':
    unittest.main()
