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

def setup_db_with_spotify_data(spotify_client_id, spotify_secret_key, artists):
    try:
        db_path = test_db_utils.create_and_populate_db_with_spotify(spotify_client_id, spotify_secret_key, artists)
    except FileNotFoundError as e:
        print("Please run cli.py from project directory!")
        sys.exit(1)
    return db_path

def setup_db():
    try:
        db_path = test_db_utils.create_and_populate_db()
    except FileNotFoundError as e:
        print("Please run cli.py from project directory!")
        sys.exit(1)
    return db_path

def run_app(db_path):
    player_controller = DummyController()
    system_entry = SystemEntry(db_path, player_controller)
    print("Welcome!")
    for text in sys.stdin:
        system_entry(text)

def remove_db():
    test_db_utils.remove_db()

def main():
    print("Initializing app...")
    # If CLI is killed with ^C, ensure the test database is removed
    def handle_sigint(sig_no, frame):
        remove_db()
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_sigint)

    if len(sys.argv) == 3:
        spotify_client_id, spotify_secret_key = sys.argv[1], sys.argv[2]
        test_artists = ["Raveena", "Ariana Grande", "U2"]
        db_path = setup_db_with_spotify_data(spotify_client_id, spotify_secret_key, test_artists)

    else:
        db_path = setup_db()

    print("Running app...")
    run_app(db_path)
    remove_db()


if __name__ == "__main__":
    main()