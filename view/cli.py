"""
This is an executable script that serves as a
CLI for interacting with the system.

Execution:
    cd bin/
    python3 cli

Example sentences:
        "Play Despacito"
        "Play some jazz music"
        "Play some faster music"
        "Who is the the saxophone player?
        "Play her top songs"

"""
import sys

from player_adaptor.dummy_adaptor import DummyController

sys.path.append('../')
from controller.system_entry import SystemEntry

db_path = '../tests/test.db'
player_controller = DummyController()
system_entry = SystemEntry(db_path, player_controller)
for text in sys.stdin:
    system_entry(text)
