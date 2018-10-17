import unittest
from unittest.mock import MagicMock

import os

from nlp.nlp_layer import NLP
from knowledge_base.api import KnowledgeBaseAPI


class TestNLP(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"
        self.nlp = NLP(self.DB_path)

    def test_parse_input_play(self):
        """Test that `control_play` intention is parsed."""
        output = self.nlp.parse_input('play the clash')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), "clash")

    def test_parse_input_query(self):
        output = self.nlp.parse_input('Who is this artist')
        self.assertEqual(str(output[0]), "['query_artist']")
        self.assertEqual(str(output[1]), '')

    def test_parse_input_KB_API(self):
        KnowledgeBaseAPI.get_all_music_entities = MagicMock(return_value=['The Who'])
        self.nlp = NLP(self.DB_path)  # Re-instantiate nlp so it uses the mock value.
        output = self.nlp.parse_input('play the who')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), 'The Who')


if __name__ == '__main__':
    unittest.main()
