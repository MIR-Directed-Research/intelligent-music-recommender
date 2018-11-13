import os
import sqlite3
import subprocess

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


if __name__ == "__main__":
    create_and_populate_db()