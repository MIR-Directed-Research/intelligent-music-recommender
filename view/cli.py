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
import signal
import sys

sys.path.append('../')
sys.path.append('.')
from player_adaptor.dummy_adaptor import DummyController
from scripts import test_db_utils
from controller.system_entry import SystemEntry

# If CLI is killed with ^C, ensure the test database is removed
def handle_sigint(sig_no, frame):
    test_db_utils.remove_db()
    sys.exit(0)
signal.signal(signal.SIGINT, handle_sigint)

try:
    db_path = test_db_utils.create_and_populate_db()
except FileNotFoundError as e:
    print("Please run cli.py from project directory!")
    sys.exit(1)

player_controller = DummyController()
system_entry = SystemEntry(db_path, player_controller)
for text in sys.stdin:
    system_entry(text)

test_db_utils.remove_db()
