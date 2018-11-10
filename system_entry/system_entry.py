import sys

from commands.interactions import Interactions
from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP


class SystemEntry:
    """This class serves as the interface through which
    a UI can send user-input to the system.

    """

    def __init__(self, db_path, player_controller):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)
        self.interactions = Interactions(self.DB_path, player_controller)
        self.nlp = NLP(self.DB_path, self.interactions.keywords)

    def __call__(self, raw_input: str):
        """The system's entrypoint.

        Call this function with a string of raw user-
        input.

        Args:
            raw_input: User input.

        """
        commands, subjects, remaining_text = self.nlp(raw_input)
        # TODO: Change these stderr outputs to logging.
        # print('Matching DB Entities:\t{}'.format(subjects if subjects else 'NONE'), file=sys.stderr)
        # print('Remaining Text:\t\t\t{}'.format(remaining_text if remaining_text else 'NONE'), file=sys.stderr)
        # print('Commands:\t\t\t\t{}'.format(commands if commands else 'NONE'), file=sys.stderr)
        self.interactions(subjects=subjects,
                          commands=commands,
                          remaining_text=remaining_text,
                          )
