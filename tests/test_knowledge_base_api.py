import unittest
from knowledge_base.api import KnowledgeBaseAPI

class TestMusicKnowledgeBaseAPI(unittest.TestCase):
    def setUp(self):
        # TODO: ensure test.db exists?
        self.kb_api = KnowledgeBaseAPI("test.db")

    def test_get_song_data(self):
        self.kb_api.open_connection()
        res = self.kb_api.get_song_data("Despacito")
        self.kb_api.close_connection()

        assert res == ('Despacito', 'Justin Bieber')

    def test_get_song_data_dne(self):
        self.kb_api.open_connection()
        res = self.kb_api.get_song_data("Not In Database")
        self.kb_api.close_connection()

        assert res == None

    def test_get_song_data_no_open_connection(self):
        res = self.kb_api.get_song_data("Not In Database")
        assert res == None
