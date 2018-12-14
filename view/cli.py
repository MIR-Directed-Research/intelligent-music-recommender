"""
This is an executable script that serves as a
CLI for interacting with the system.

Execution:
    cd intelligent-music-recommender/

    # For use with default Knowledge Base:
    python3 cli

    # For use with another Knowledge Base:
    python3 cli -d ./some_other_knowledgebase.db

Example sentences:
        "Play Despacito"
        "Play some jazz music"
        "Play some faster music"
        "Who is the the saxophone player?
        "Play her top songs"

"""
import os
import sys
from argparse import ArgumentParser

sys.path.append('../')
sys.path.append('.')
from player_adaptor.dummy_adaptor import DummyController
from controller.system_entry import SystemEntry

DEFAULT_DB = "./knowledge_base/knowledge_base.db"


def run_app(db_path, nlp_parser):
    player_controller = DummyController()
    system_entry = SystemEntry(db_path=db_path,
                               player_controller=player_controller,
                               parser_type=nlp_parser,
                               )
    print("Welcome!")
    for text in sys.stdin:
        system_entry(text)


def main():
    print("Initializing app...")

    parser = ArgumentParser()
    parser.add_argument("-d", nargs="?", type=str, dest="db_path",
                        help=" Specifies a relative path to the DB, (include "
                             "the filename). Ex: -d ./some_db.sql")
    parser.add_argument("-t", "--tree_parser",
                        help=" Use a 'Tree' parser instead of a 'Bag of Words'"
                             "parser.  The tree parser uses a Context Free"
                             "Grammar to parse the input into a tree of command"
                             "expressions."                                                   "",
                        action="store_true")
    args = parser.parse_args()

    db_path = args.db_path or DEFAULT_DB

    if not os.path.isfile(db_path):
        print("Error: DB file \"{}\" not found. Ensure your working directory "
              "is the app root, and that the DB filepath is specified "
              "relative to this location.".format(db_path),
              file=sys.stderr)
        sys.exit()

    nlp_parser = 'TREE' if args.tree_parser else 'BagOfWords'

    print("Running app...")
    run_app(db_path, nlp_parser)


if __name__ == "__main__":
    main()
