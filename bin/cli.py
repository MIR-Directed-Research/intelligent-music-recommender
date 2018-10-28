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

from player_controller.dummy_controller import DummyController

sys.path.append('../')
from system_entry.system_entry import SystemEntry

db_path = '../tests/test.db'
player_controller = DummyController()
system_entry = SystemEntry(db_path, player_controller)
for text in sys.stdin:
    import pydevd; pydevd.settrace('localhost', port=8081, stdoutToServer=True, stderrToServer=True)
    system_entry(text)
