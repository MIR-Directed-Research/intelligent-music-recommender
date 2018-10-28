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
from tests.test_play_controller import TestUIConnector

if __name__ == '__main__':
    unittest.main()
