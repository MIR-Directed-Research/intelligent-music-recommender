from command_evaluation.bag_of_words_eval_engine import BOWEvalEngine
from command_evaluation.tree_eval_engine import TreeEvalEngine
from knowledge_base.api import KnowledgeBaseAPI
from nlp.bag_of_words_parser import BOWParser
from nlp.tree_parser import TreeParser


class SystemEntry:
    """This class serves as the interface through which
    a UI can send user-input to the system.

    """

    def __init__(self, db_path, player_controller, parser_type='BagOfWords'):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)
        self.parser_type = parser_type
        if parser_type == 'BagOfWords':
            self.eval_engine = BOWEvalEngine(self.DB_path, player_controller)
            self.parser = BOWParser(self.DB_path, self.eval_engine.keywords)
        elif parser_type == 'TREE':
            self.eval_engine = TreeEvalEngine(self.DB_path, player_controller)
            self.parser = TreeParser(self.DB_path, self.eval_engine.keywords)

    def __call__(self, raw_input: str):
        """The system's entrypoint.

        Call this function with a string of raw user-
        input.

        Args:
            raw_input: User input.

        """
        if self.parser_type == 'BagOfWords':
            self.eval_engine(*self.parser(raw_input))
        elif self.parser_type == 'TREE':
            self.eval_engine(self.parser, raw_input)
