import os
import pprint
import subprocess
import sys

sys.path.append('../')  # if running this script from 'scripts/' directory
sys.path.append('.')  # if running this script from project root
sys.path.append('./scripts')  # if running this script from project root
from knowledge_base.api import KnowledgeBaseAPI
from scripts.spotify_client import SpotifyClient

pp = pprint.PrettyPrinter(
    indent=2,
    depth=2,  # hide items nested past 3 levels
    compact=True,  # fit as many items into a single line as possible
)

TEST_DB_NAME = "test.db"
SCHEMA_FILE_NAME = "schema.sql"
TEST_DATA_FILE_NAME = "test_data.sql"


def exec_sql_script(db_path, path_to_sql_file, DB_name: str = None):
    """Equivalent to running the following command in terminal:
        $ sqlite3 path_to_test_db_file < schema_file.sql

    Params:
        path_prefix (string): specifies directory to test db (creating it if dne).
        path_to_sql_file (string): path to sql script.
    """
    with open(path_to_sql_file) as f:
        subprocess.run(["sqlite3", db_path], stdin=f)


def create_and_populate_db(path: str = None):
    """Creates and fills sqlite database, saving .db file to 'tests/'
   directory, unless another path is specified.

   Tries to find SQL scripts depending on where this module is invoked from.

   Returns:
       (string): (relative) path to newly created .db file.
   """
    test_db_path_prefix, scripts_path_prefix = _get_path_prefixes()
    db_path = path or (test_db_path_prefix + TEST_DB_NAME)

    exec_sql_script(db_path, scripts_path_prefix + SCHEMA_FILE_NAME)
    exec_sql_script(db_path, scripts_path_prefix + TEST_DATA_FILE_NAME)
    return db_path


def create_db(path: str = None):
    """Creates sqlite db file, saving it to 'tests/' directory.

    NOTE: copy+paste (near) duplicate of create_and_populate_db.

    Tries to find SQL scripts depending on where this module is invoked from.

    Returns:
        (string): (relative) path to newly created .db file.
    """
    test_db_path_prefix, scripts_path_prefix = _get_path_prefixes()
    db_path = path or (test_db_path_prefix + TEST_DB_NAME)

    exec_sql_script(db_path, scripts_path_prefix + SCHEMA_FILE_NAME)
    return db_path


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
    return subprocess.run(["rm", test_db_path + TEST_DB_NAME]).returncode == 0


def get_artist_data(spotify, artists):
    """
    Params:
        spotify (SpotifyClient): for making requests to Spotify web API.
        artists (iterable): each element is an artist name.
            (e.g. list of strings, file with artist names on each line)

    Returns:
        artist_data (dict): key is artist name, value is a dict containing artist metadata.
            e.g. {
                "Justin Bieber": {
                    id=1uNFoZAHBGtllmzznpCI3s,
                    num_followers=25683438,
                    genres=["canadian pop", "dance pop", "pop", "post-teen pop"]
                }
                ...
            }
    """
    artist_data = dict()
    for tmp_artist_name in artists:
        tmp_artist_name = tmp_artist_name.strip()
        data = spotify.get_artist_data(tmp_artist_name)
        if data is not None:
            artist_data[tmp_artist_name] = data
    return artist_data


def get_artist_metadata(spotify, artist_names):
    """Fetches metadata for each artists specified in stdin.

    Returns:
        full_artist_metadata (dict): key is artist name, val is dict with:
            Spotify ID, genres, number of Spotify followers, related artists, and songs.

    e.g. {
        "Raveena": {
            'ID': '2kQnsbKnIiMahOetwlfcaS',
            'genres': ['indie r&b'],
            'num_followers': 19191,
            'related_artists': {
                'Alextbh': {
                    'ID': '0kXDB5aeESWj5BD9TCLkMu',
                    'genres': ['indie r&b', 'malaysian indie'],
                    'num_followers': 19517
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
    artist_summaries = get_artist_data(spotify, artist_names)
    full_artist_metadata = dict()
    for artist, artist_summary in artist_summaries.items():
        full_artist_metadata[artist] = dict(
            ID=artist_summary["id"],
            num_followers=artist_summary["num_followers"],
            genres=artist_summary["genres"],
            related_artists=spotify.get_related_artists(artist_summary["id"]),
            songs=spotify.get_top_songs(artist_summary["id"], "CA")
        )
    return full_artist_metadata


def create_and_populate_db_with_spotify(spotify_client_id, spotify_secret_key, artists, path=None):
    path_to_db = create_db(path=path)
    artist_metadata = get_artist_metadata(SpotifyClient(spotify_client_id, spotify_secret_key), artists)
    kb_api = KnowledgeBaseAPI(path_to_db)
    for artist_name, artist_info in artist_metadata.items():
        kb_api.add_artist(artist_name, artist_info["genres"], artist_info["num_followers"])

        for song_name, song_info in artist_info["songs"].items():
            kb_api.add_song(
                song_name,
                artist_name,
                song_info["popularity"],
                song_info["duration_ms"],
            )

        for rel_artist_name, rel_artist_info in artist_info["related_artists"].items():
            kb_api.add_artist(rel_artist_name, rel_artist_info["genres"], rel_artist_info["num_followers"])
            kb_api.connect_entities(artist_name, rel_artist_name, "similar to", 100)
            kb_api.connect_entities(rel_artist_name, artist_name, "similar to", 100)
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
