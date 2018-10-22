import os
import unittest
from unittest.mock import MagicMock

from knowledge_base.api import KnowledgeBaseAPI
from play_controller.controller import Controller


class TestPlayController(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"
        self.controller = Controller(db_path=self.DB_path)

    def test_call(self):
        save_state = KnowledgeBaseAPI.get_all_music_entities
        KnowledgeBaseAPI.get_all_music_entities = MagicMock(return_value=['The Who'])
        controller = Controller(db_path=self.DB_path)
        result = controller('play test')
        self.assertEqual(result, ["Sorry, I don't understand"])
        KnowledgeBaseAPI.get_all_music_entities = save_state

    def test_call_functional_test(self):
        result = self.controller('play justin bieber')
        self.assertEqual(result, ["Playing Justin Bieber"])


if __name__ == '__main__':
    unittest.main()
