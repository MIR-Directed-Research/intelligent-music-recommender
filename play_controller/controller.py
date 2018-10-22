import sys

from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP
from play_controller.interactions import Interactions


class Controller:
    def __init__(self, db_path):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)
        self.interactions = Interactions(self.DB_path)
        self.nlp = NLP(self.DB_path, self.interactions.keywords)

    def __call__(self, raw_input):
        command_lst, db_subject, remaining_text = self.nlp(raw_input)
        actions = self.interactions.actions
        results = []
        for command in command_lst:
            func = actions.get(command, self.interactions.default)
            print('Matching DB Entity:\t{}'.format(db_subject if db_subject else 'NONE'), file=sys.stderr)
            print('Remaining Text:\t\t{}'.format(remaining_text if remaining_text else 'NONE'), file=sys.stderr)
            print('Command:\t\t\t{}'.format(command if command else 'NONE'), file=sys.stderr)
            results.append(func(
                db_subject=db_subject,
                remaining_text=remaining_text
            ))
        return results
