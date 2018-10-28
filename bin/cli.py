"""
Run this script from within the /bin directory:

cd bin/
python3 cli
"""
import sys

from player_controller.dummy_controller import DummyController

sys.path.append('../')
from ui_connector.uiconnector import UIConnector

db_path = '../tests/test.db'
player_controller = DummyController()
ui_connector = UIConnector(db_path, player_controller)
for text in sys.stdin:
    ui_connector(text)
