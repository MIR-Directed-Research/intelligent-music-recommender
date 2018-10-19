import os
import unittest
from unittest.mock import MagicMock

from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP
from play_controller.commands import intentions


class TestNLP(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"
        self.keywords = {k: v[0] for k, v in intentions.items()}
        self.nlp = NLP(db_path=self.DB_path,
                       keywords=self.keywords)

    def test_parse_input_play(self):
        """Test that `control_play` intention is parsed."""
        output = self.nlp('play the clash')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), "clash")

    def test_parse_input_query(self):
        output = self.nlp('Who is this artist')
        self.assertEqual(str(output[0]), "['query_artist']")
        self.assertEqual(str(output[1]), '')

    def test_parse_input_KB_API(self):
        KnowledgeBaseAPI.get_all_music_entities = MagicMock(return_value=['The Who'])
        self.nlp = NLP(self.DB_path, self.keywords)  # Re-instantiate nlp so it uses the mock value.
        output = self.nlp('play the who')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), 'The Who')


if __name__ == '__main__':
    unittest.main()
