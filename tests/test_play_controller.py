import os
import unittest
from unittest.mock import MagicMock

from knowledge_base.api import KnowledgeBaseAPI
from tests.mock_objects import MockController
from ui_connector.uiconnector import UIConnector


class TestUIConnector(unittest.TestCase):
    def setUp(self):
        self.DB_path = "tests/test.db"
        # Check working directory, update path to DB accordingly.
        if os.getcwd().split('/')[-1] == 'tests':
            self.DB_path = "test.db"
        self.results_dict = {}
        self.player_controller = MockController(self.results_dict)
        self.ui_connector = UIConnector(db_path=self.DB_path,
                                        player_controller=self.player_controller,
                                        )

    def test_call(self):
        save_state = KnowledgeBaseAPI.get_all_music_entities
        KnowledgeBaseAPI.get_all_music_entities = MagicMock(return_value=['The Who'])
        controller = UIConnector(db_path=self.DB_path,
                                 player_controller=self.player_controller,
                                 )
        controller('play test')
        self.assertEqual(self.results_dict['respond'], "Sorry, I don't understand")
        KnowledgeBaseAPI.get_all_music_entities = save_state

    def test_call_functional_test(self):
        self.results_dict['play'] = None
        self.ui_connector('play justin bieber')
        self.assertEqual(self.results_dict['play'], ['Justin Bieber'])


if __name__ == '__main__':
    unittest.main()
