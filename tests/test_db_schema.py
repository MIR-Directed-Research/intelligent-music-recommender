from contextlib import closing
from knowledge_base.api import KnowledgeBaseAPI
import os
import unittest

class TestDbSchema(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    def test_rejects_unknown_entity(self):
        res = self.kb_api.connect_entities("Unknown Entity", "Justin Timberlake", "similar to", 0)
        self.assertEqual(res, False,
            "Expected attempt to connect an unknown entity to fail.")

        res = self.kb_api.get_similar_entities("Unknown Entity")
        self.assertEqual(res, [])

    def test_rejects_unknown_relation(self):
        res = self.kb_api.connect_entities("Shawn Mendes", "Justin Timberlake", "unknown relation", 0)
        self.assertEqual(res, False,
            "Expected attempt to connect entities with unknown relation to fail.")

    def test_rejects_score_out_of_range(self):
        res = self.kb_api.connect_entities("Justin Timberlake", "Justin Timberlake", "similar to", -1)
        self.assertEqual(res, False,
            "Expected attempt to connect entities with score out-of-range to fail.")

        res = self.kb_api.get_similar_entities("Justin Timberlake")
        self.assertEqual(len(res), 0)

    def test_rejects_duplicate_edge(self):
        res = self.kb_api.connect_entities("Justin Bieber", "Justin Timberlake", "similar to", 1)
        self.assertEqual(res, False,
            "Expected attempt to add a duplicate edge to fail.")

    def test_edges_not_null_constraints(self):
        res = self.kb_api.connect_entities(None, "Justin Timberlake", "similar to", 1)
        self.assertEqual(res, False,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.connect_entities("U2", "U2", None, 1)
        self.assertEqual(res, False,
            "Expected 'None' value for edge type to be rejected.")

        res = self.kb_api.connect_entities("U2", "U2", "similar to", None)
        self.assertEqual(res, False,
            "Expected 'None' value for edge score to be rejected.")

    def test_entities_not_null_constraints(self):
        res = self.kb_api.add_artist(None)
        self.assertEqual(res, False,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.add_song("Song name", None)
        self.assertEqual(res, False,
            "Expected 'None' value for artist to be rejected.")

        res = self.kb_api.add_song(None, "Artist name")
        self.assertEqual(res, False,
            "Expected 'None' value for artist to be rejected.")

        node_id = self.kb_api._add_node(None, "artist")
        self.assertEqual(node_id, None,
            "Expected 'None' value for entity name to be rejected.")

        node_id = self.kb_api._add_node("Some entity", None)
        self.assertEqual(node_id, None,
            "Expected 'None' value for entity type to be rejected.")

if __name__ == '__main__':
    unittest.main()
