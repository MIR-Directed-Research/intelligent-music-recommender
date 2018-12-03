import os
import pprint
import sqlite3
import subprocess
import sys


sys.path.append('../')  # if running this script from 'scripts/' directory
sys.path.append('.')    # if running this script from project root
sys.path.append('./scripts')    # if running this script from project root
from knowledge_base.api import KnowledgeBaseAPI
from spotify_client import SpotifyClient

pp = pprint.PrettyPrinter(
    indent=2,
    depth=2,        # hide items nested past 3 levels
    compact=True,   # fit as many items into a single line as possible
)


TEST_DB_NAME = "test.db"
SCHEMA_FILE_NAME = "schema.sql"
TEST_DATA_FILE_NAME = "test_data.sql"

def exec_sql_script(path_prefix, path_to_sql_file):
    """Equivalent to running the following command in terminal:
        $ sqlite3 path_to_test_db_file < schema_file.sql

    Params:
        path_prefix (string): specifies directory to test db (creating it if dne).
        path_to_sql_file (string): path to sql script.
    """
    with open(path_to_sql_file) as f:
        subprocess.run(["sqlite3", path_prefix+TEST_DB_NAME], stdin=f)

def create_and_populate_db():
    """Creates and fills sqlite database, saving .db file to 'tests/' directory

    Tries to find SQL scripts depending on where this module is invoked from.

    Returns:
        (string): (relative) path to newly created .db file.
    """
    test_db_path_prefix, scripts_path_prefix = _get_path_prefixes()
    exec_sql_script(test_db_path_prefix, scripts_path_prefix + SCHEMA_FILE_NAME)
    exec_sql_script(test_db_path_prefix, scripts_path_prefix + TEST_DATA_FILE_NAME)
    return test_db_path_prefix + TEST_DB_NAME

def create_db():
    """Creates sqlite db file, saving it to 'tests/' directory.

    NOTE: copy+paste (near) duplicate of create_and_populate_db.

    Tries to find SQL scripts depending on where this module is invoked from.

    Returns:
        (string): (relative) path to newly created .db file.
    """
    test_db_path_prefix, scripts_path_prefix = _get_path_prefixes()
    exec_sql_script(test_db_path_prefix, scripts_path_prefix + SCHEMA_FILE_NAME)
    return test_db_path_prefix + TEST_DB_NAME

def _get_path_prefixes():
    # Used for adjusting path based on where the script is run from.
    cur_dir = os.getcwd().split("/")[-1]

    # From tests folder in project root dir
    if cur_dir == "tests":
        test_db_path_prefix = ""
        scripts_path_prefix = "../scripts/"

    # From scripts folder in project root dir
    elif cur_dir == "scripts":
        test_db_path_prefix = "../tests/"
        scripts_path_prefix = ""

    # From project root dir
    else:
        test_db_path_prefix = "tests/"
        scripts_path_prefix = "scripts/"
    return test_db_path_prefix, scripts_path_prefix

def remove_db():
    "Returns True if command succeeded, False otherwise."
    test_db_path, _ = _get_path_prefixes()
    return subprocess.run(["rm", test_db_path+TEST_DB_NAME]).returncode == 0

def get_artist_IDs(spotify, artists):
    """
    Params:
        spotify (SpotifyClient): for making requests to Spotify web API.
        artists (iterable): each element is an artist name.
            (e.g. list of strings, file with artist names on each line)

    Returns:
        artist_by_id (dict): key is artist name, value is their Spotify ID.
        e.g. {
            "Raveena": '2kQnsbKnIiMahOetwlfcaS',
            ...
        }
    """
    artist_by_id = dict()
    for tmp_artist_name in artists:
        tmp_artist_name = tmp_artist_name.strip()
        tmp_ID = spotify.get_artist_id(tmp_artist_name)
        if tmp_ID is not None:
            artist_by_id[tmp_artist_name] = tmp_ID
    return artist_by_id

def get_artist_metadata(spotify, artist_names):
    """Fetches metadata for each artists specified in stdin.

    Returns:
        artist_metadata (dict): key is artist name, val is dict with:
            Spotify ID, related artists, and songs.

    e.g. {
        "Raveena": {
            'ID': '2kQnsbKnIiMahOetwlfcaS',
            'related_artists': {
                'Alextbh': {
                    'ID': '0kXDB5aeESWj5BD9TCLkMu',
                    'genres': ['indie r&b', 'malaysian indie'],
                    'numFollowers': 19517
                },
                ...
            },
            'songs': {
                'Honey': {
                    'duration_ms': 272331,
                    'id': '6ohzjop0VYBRZ12ichlwg5',
                    'popularity': 60,
                    'uri': 'spotify:track:6ohzjop0VYBRZ12ichlwg5'
                },
                ...
            }
        }
        ...

    """
    # TODO: fill and check cache (e.g. pickle file) for Spotify data to avoid unnecessary network latency
    artist_ids = get_artist_IDs(spotify, artist_names)
    artist_metadata = dict()
    for artist, artist_ID in artist_ids.items():
        artist_metadata[artist] = dict(
            ID=artist_ID,
            related_artists=spotify.get_related_artists(artist_ID),
            songs=spotify.get_top_songs(artist_ID, "CA")
        )
    return artist_metadata

def create_and_populate_db_with_spotify(spotify_client_id, spotify_secret_key, artists):
    path_to_db = create_db()

    print("Fetching artist metadata from Spotify...")
    artist_metadata = get_artist_metadata(SpotifyClient(spotify_client_id, spotify_secret_key), artists)
    pp.pprint(artist_metadata)

    kb_api = KnowledgeBaseAPI(path_to_db)
    for artist_name, artist_info in artist_metadata.items():
        kb_api.add_artist(artist_name)

        for song_name, _ in artist_info["songs"].items():
            kb_api.add_song(song_name, artist_name)

        for rel_artist_name, _ in artist_info["related_artists"].items():
            kb_api.add_artist(rel_artist_name)
            kb_api.connect_entities(artist_name, rel_artist_name, "similar to", 100)
            kb_api.connect_entities(rel_artist_name, artist_name, "similar to", 100)

    for artist_name, _ in artist_metadata.items():
        print("Artist", artist_name, "is similar to", kb_api.get_similar_entities(artist_name))
    return path_to_db

def main():
    print("Enter Spotify client ID:")
    spotify_client_id = sys.stdin.readline().split(" ")[-1].strip("\n")
    print("Enter Spotify secret key:")
    spotify_secret_key = sys.stdin.readline().split(" ")[-1].strip("\n")

    print("Enter names of artists, separated by new-lines:")
    create_and_populate_db_with_spotify(spotify_client_id, spotify_secret_key, sys.stdin)


if __name__ == "__main__":
    main()