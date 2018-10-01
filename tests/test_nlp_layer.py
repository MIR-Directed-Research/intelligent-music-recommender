import unittest
from unittest.mock import MagicMock
from nlp.nlp_layer import NLP
from knowledge_base.api import KnowledgeBaseAPI


class TestNLP(unittest.TestCase):
    def setUp(self):
        self.nlp = NLP()

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
        KnowledgeBaseAPI.get_all_nouns = MagicMock(return_value=['The Who'])
        self.nlp = NLP()  # Re-instantiate nlp so it uses the mock value.
        output = self.nlp.parse_input('play the who')
        self.assertEqual(str(output[0]), "['control_play']")
        self.assertEqual(str(output[1]), 'The Who')

if __name__ == '__main__':
    unittest.main()
