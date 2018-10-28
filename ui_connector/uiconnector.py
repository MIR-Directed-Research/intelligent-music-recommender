import sys

from commands.interactions import Interactions
from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP


class UIConnector:
    def __init__(self, db_path, player_controller):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)
        self.interactions = Interactions(self.DB_path, player_controller)
        self.nlp = NLP(self.DB_path, self.interactions.keywords)

    def __call__(self, raw_input):
        commands, subjects, remaining_text = self.nlp(raw_input)
        results = []
        print('Matching DB Entities:\t{}'.format(subjects if subjects else 'NONE'), file=sys.stderr)
        print('Remaining Text:\t\t\t{}'.format(remaining_text if remaining_text else 'NONE'), file=sys.stderr)
        print('Commands:\t\t\t\t{}'.format(commands if commands else 'NONE'), file=sys.stderr)
        self.interactions(subjects=subjects,
                          commands=commands,
                          remaining_text=remaining_text,
                          )
        return results
