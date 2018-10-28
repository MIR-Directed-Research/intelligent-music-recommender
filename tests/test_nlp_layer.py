import os
import unittest
from unittest.mock import MagicMock

from commands.interactions import Interactions
from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP
from tests.mock_objects import MockController


class TestNLP(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"

        self.kb_api = KnowledgeBaseAPI(self.DB_path)
        self.results_dict = {}
        self.player_controller = MockController(self.results_dict)
        self.interactions = Interactions(self.DB_path, self.player_controller)
        self.nlp = NLP(self.DB_path, self.interactions.keywords)
        self.keywords = self.interactions.keywords

    def test_parse_input_play(self):
        """Test that `control_play` intention is parsed."""
        output = self.nlp('play the clash')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), '[]')
        self.assertEqual(str(output[2]), 'clash')

    def test_parse_input_query(self):
        output = self.nlp('Who is this artist')
        self.assertEqual(str(output[0]), "['query_artist']")
        self.assertEqual(str(output[1]), '[]')

    def test_parse_input_KB_API(self):
        save_state = KnowledgeBaseAPI.get_all_music_entities
        KnowledgeBaseAPI.get_all_music_entities = MagicMock(return_value=['The Who'])
        nlp = NLP(self.DB_path, self.keywords)  # Re-instantiate nlp so it uses the mock value.
        output = nlp('play the who')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), "['The Who']")
        self.assertEqual(str(output[2]), '')
        KnowledgeBaseAPI.get_all_music_entities = save_state

    def test_call_functional_test(self):
        output = self.nlp('play Justin bieber')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), "['Justin Bieber']")
        self.assertEqual(str(output[2]), '')


if __name__ == '__main__':
    unittest.main()
