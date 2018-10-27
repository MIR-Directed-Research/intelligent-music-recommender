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
        self.assertTrue(res is None, "Expected 'None' result for queried song not in DB.")

    def test_find_similar_song(self):
        res = self.kb_api.get_similar_entities("Despacito")
        self.assertEqual(
            len(res), 1,
            "Expected only one song similar to \"Despacito\".",
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

    def test_connect_entities(self):
        res = self.kb_api.get_similar_entities("Shawn Mendes")
        self.assertEqual(len(res), 0)

        res = self.kb_api.connect_entities("Shawn Mendes", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, True, "")

        res = self.kb_api.get_similar_entities("Shawn Mendes")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "Justin Timberlake")


if __name__ == '__main__':
    unittest.main()
