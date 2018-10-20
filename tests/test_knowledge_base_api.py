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


if __name__ == '__main__':
    unittest.main()
