import unittest

from controller.system_entry import SystemEntry
from scripts import test_db_utils
from tests.mock_objects import MockController


class TestSystemEntryTreeParser(unittest.TestCase):
    def setUp(self):
        self.DB_path = test_db_utils.create_and_populate_db()
        self.results_dict = {}
        self.player_controller = MockController(self.results_dict)
        self.system_entry = SystemEntry(db_path=self.DB_path,
                                        player_controller=self.player_controller,
                                        parser_type="TREE")

    def tearDown(self):
        test_db_utils.remove_db()

    def test_call_functional_test(self):
        self.results_dict['play'] = None
        self.system_entry('play justin bieber')
        self.assertEqual(self.results_dict['play'], ['Justin Bieber'])

    def test_call_similarity_functional_test(self):
        self.results_dict['respond'] = None
        self.system_entry('who are artists like justin bieber')
        self.assertTrue('Justin Timberlake' in self.results_dict['respond'])
        self.assertTrue('Shawn Mendes' in self.results_dict['respond'])

        self.results_dict['play'] = None
        self.system_entry('play some songs like despacito')
        self.assertTrue('Rock Your Body' in self.results_dict['play'])


if __name__ == '__main__':
    unittest.main()
