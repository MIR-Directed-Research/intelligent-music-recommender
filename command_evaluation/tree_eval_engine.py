import sys
from collections import OrderedDict
from typing import List

import nltk

from knowledge_base.api import KnowledgeBaseAPI


class EvalEngine:
    """This class stores the possible interactions between the
    user and the system, and the logic to act on them.

    The `intents` property contains a mapping that stores
    signifiers of user's intent, along with the functions
    that they map to.

    This class also contains the functions that corresponds to
    each of the possible user interactions.

    """

    def __init__(self, db_path, player_controller):
        self.player = player_controller
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    def __call__(self, nltk_parse_tree):
        """Initiates a sequence of commands that will act
        on the subject parameters in order of command
        precedence.

        Args:
            subjects: List of subjects in the database.
            commands: Names of commands to enact.
            remaining_text: Any remaining text not parsed by the NLP layer.

        Returns:

        """
        # Call the highest precedence command.
        self._eval(nltk_parse_tree)

    @property
    def unary_commands(self):
        """Returns a mapping that stores signifiers of user's
        intent, along with the `commands` and the functions
        that they map to.

        The ordering of these commands matters, as it is used to
        store the precedence of operations.

        Returns (OrderedDict): A mapping of intentions, their
            corresponding signifiers (as keywords), and function
            handlers.

        """
        return OrderedDict([
            ('control_forward', (['skip', 'next'], self._control_skip)),
            ('query_similar_entities', (['like', 'similar'], self._query_similar_entities)),
        ])

    @property
    def terminal_commands(self):
        return OrderedDict([
            ('query_commands', (['hi', 'how', 'hello'], self._query_commands)),
            ('control_stop', (['stop'], self._control_stop)),
            ('control_pause', (['pause'], self._control_pause)),
            ('control_play', (['start', 'play'], self._control_play)),
            ('query_artist', (['who', 'artist'], self._query_artist)),

        ])

    @property
    def binary_commands(self):
        return OrderedDict([
            ('control_intersection', (['and'], self._control_intersection)),
            ('control_union', (['or'], self._control_union)),
        ])

    @property
    def keywords(self):
        """For each type of command, generate a dictionary
        of keywords that map to the specific command (intent)

        """
        return {
            "unary": {
                k: v[0] for k, v in self.unary_commands.items()
            },
            "terminal": {
                k: v[0] for k, v in self.terminal_commands.items()
            },
            "binary": {
                k: v[0] for k, v in self.binary_commands.items()
            },
        }

    @property
    def actions(self):
        return {k: v[1] for k, v in self.unary_commands.items()}

    @property
    def command_precedence(self):
        return [k for k, v in self.unary_commands.items()]

    def _query_commands(self, entities):
        """Terminal command. Reports on possible commands and interactions.

        """
        if entities:
            # Handle question about specific `subjects`.
            self.player.respond("I'm sorry, I can't answer that one")
        else:
            # Handle genery inquiries.
            self.player.respond("Hi there! Ask me to play artists or songs. "
                                "I can also find songs that are similar to other "
                                "artists.")

    def _control_play(self, entities: List):
        """Terminal command. Plays the subjects specified.

       TODO:
           - query db for entity
               - if it's of type song, play it
               - if it's anything else, get the songs associated with
                 it and play in DESC order
        """
        if entities:
            self.player.play(entities)
        else:
            self.player.respond("I'm sorry, I couldn't find that for you.")

    def _control_stop(self):
        self.player.stop()

    def _control_pause(self):
        self.player.pause()

    def _control_skip(self):
        self.player.skip()

    def _control_intersection(self):
        self.player.skip()

    def _control_union(self):
        self.player.skip()

    def _query_artist(self, entities):
        self.player.respond(entities)

    def _query_similar_entities(self, subjects):
        similar_entities = []
        for e in subjects:
            similar_entities += self.kb_api.get_related_entities(e)

        return similar_entities

    def _eval(self, tree: nltk.tree.Tree):
        """Calls the next function in the commands parameter.

        """

        """
        Root -> Terminal_Command Result
        Result -> Entity
        Result -> Unary_Command Result
        Result -> Result Binary_Command Result
        Entity -> '{}'
        Unary_Command -> '{}'
        Terminal_Command -> '{}'
        Binary_Command -> '{}'

        "play something similar to u2"

        (Root
          (Terminal_Command control_play)
          (Result
            (Unary_Command query_similar_entities)
            (Result (Entity U2))))
        """

        if tree.label() == "Root":
            func = self._eval(tree[0])
            result = self._eval(tree[1])
            func(result)
            return
        elif tree.label() == "Result":
            if tree[0].label() == "Entity":
                return self._eval(tree[0])
            if tree[0].label() == "Unary_Command":
                func = self._eval(tree[0])
                result = self._eval(tree[1])
                return func(result)
            if tree[1].label() == "Binary_Command":
                result_left = self._eval(tree[0])
                func = self._eval(tree[1])
                result_right = self._eval(tree[2])
                return func(result_left, result_right)
        elif tree.label() == "Unary_Command":
            func = self.unary_commands.get(tree[0])[1]
            return func
        elif tree.label() == "Terminal_Command":
            func = self.terminal_commands.get(tree[0])[1]
            return func
        elif tree.label() == "Binary_Command":
            func = self.binary_commands.get(tree[0])[1]
            return func
        elif tree.label() == "Entity":
            return [tree[0]]

        print("Error: CFG label rule not defined in "
              "command_self._evaluation.tree_self._eval_engine."
              "self._evalEngine#_eval",
              file=sys.stderr)
