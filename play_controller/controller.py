import sys

from knowledge_base.api import KnowledgeBaseAPI
from nlp.nlp_layer import NLP
from play_controller import commands


class Controller:
    def __init__(self, db_path):
        self.DB_path = db_path
        self.nlp = NLP(self.DB_path, commands.keywords)
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    def __call__(self, raw_input):
        command_lst, entity = self.nlp(raw_input)
        results = []
        for command in command_lst:
            func = commands.actions.get(command, commands.default)
            print('Entity:\t\t{}'.format(entity if entity else 'NONE'), file=sys.stdout)
            print('Command:\t{}'.format(command if command else 'NONE'), file=sys.stdout)
            results.append(func(entity))
        return results
