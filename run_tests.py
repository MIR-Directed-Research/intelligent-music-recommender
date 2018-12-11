import unittest
"""
Import your test below to have it automatically run
by this test-runner.

To run the tests:
    cd intelligent-music-recommender
    python ./run_tests.py
"""
from tests.test_nlp_layer import TestNLP
from tests.test_knowledge_base_api import TestMusicKnowledgeBaseAPI
from tests.test_system_entry_bag_of_words import TestSystemEntryBOW
from tests.test_system_entry_tree_parser import TestSystemEntryTreeParser
from tests.test_db_schema import TestDbSchema

if __name__ == '__main__':
    unittest.main()
