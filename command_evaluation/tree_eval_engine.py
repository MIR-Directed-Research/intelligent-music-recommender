import sys
from collections import OrderedDict
from typing import List

import nltk

from knowledge_base.api import KnowledgeBaseAPI


class TreeEvalEngine:
    """This class stores the possible interactions between the
    user and the system, and the logic to act on them.

    The various "Commands" properties contain mappings that store
    signifiers of user's intent, along with the functions
    that they map to.

    This class also contains the functions that corresponds to
    each of the possible user interactions.

    """

    def __init__(self, db_path, player_controller):
        self.player = player_controller
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    def __call__(self, parser, text):
        """Evaluates a parse tree that was generated by
        the NLP layer from the user input.

        Args:
            nltk_parse_tree: An NLTK Parse Tree, as defined
                by the CFG given in the "parser" function
                of the tree_parser in the NLP layer.

        """
        try:
            nltk_parse_tree = parser(text)

            self._evaluate(nltk_parse_tree)
        except:
            self.player.respond("I'm sorry, I don't understand.")

    @property
    def unary_commands(self):
        """A unary command operates on just one set of
        entities when evaluating a user's input
        (encoded as a Parse Tree).

        Returns:
            A mapping that stores signifiers of user's
            intent, along with the `commands` and the functions
            that they map to.

        """
        return OrderedDict([
            ('query_similar_entities', (['like', 'similar'], self._query_similar_entities)),
            ('query_songs_by_artist', (['songs by'], self._query_songs_by_artist)),
            ('query_artist_by_song', (['artist'], self._query_artist_by_song)),
        ])

    @property
    def terminal_commands(self):
        """A terminal commands is the final command that is
        executed on the results of evaluating a user's input
        (encoded as a Parse Tree).

        Returns:
            A mapping that stores signifiers of user's
            intent, along with the `commands` and the functions
            that they map to.

        """
        return OrderedDict([
            ('query_commands', (['hi', 'how', 'hello'], self._query_commands)),
            ('control_stop', (['stop'], self._control_stop)),
            ('control_pause', (['pause'], self._control_pause)),
            ('control_play', (['start', 'play'], self._control_play)),
            ('query_info', (['who', 'what'], self._query_info)),
            ('control_forward', (['skip', 'next'], self._control_skip)),

        ])

    @property
    def binary_commands(self):
        """A binary command operates on two sets of
        entities when evaluating a user's input
        (encoded as a Parse Tree).

        Returns:
            A mapping that stores signifiers of user's
            intent, along with the `commands` and the functions
            that they map to.

        """
        return OrderedDict([
            ('control_union', (['or', 'and'], self._control_union)),
        ])

    @property
    def keywords(self):
        """For each type of command, generate a dictionary
        of keywords that map to the specific command (intent).

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
        # TODO: make this work
        """Terminal command.

        Reports on possible commands and interactions.

        """
        if entities:
            # Handle question about specific `subjects`.
            self.player.respond("I'm sorry, I can't answer that one")
        else:
            # Handle genery inquiries.
            self.player.respond("Hi there! Ask me to play artists or songs. "
                                "I can also find songs that are similar to other "
                                "artists.")

    def _control_play(self, entities: List[str]):
        """Terminal command.

        Plays the subjects specified.

        Args:
            entities: A list of Entities.

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
        """Terminal Command

        Stops the player.

        """
        self.player.stop()

    def _control_pause(self):
        """Terminal Command

        Pauses the player.

        """
        self.player.pause()

    def _control_skip(self):
        """Terminal Command

        Skips the song.

        """
        self.player.skip()

    def _control_union(self, entities_1: List[str], entities_2: List[str]):
        """Binary Command

            Returns the intersection of the two parameters.

            Args:
                entities_1: A list of Entities.
                entities_2: A list of Entities.

            Returns: A list of Entities

            """
        return list(set(entities_1).union(set(entities_2)))

    def _query_info(self, entities: List[str]):
        """Terminal Command

        Queries the artists for each Entity.

        Args:
            entities: A list of Entities.

        """
        self.player.respond(entities)

    def _query_similar_entities(self, entities: List[str]):
        """Unary Command

        Returns a list of related Entities for
        all Entities in the parameters.

        Args:
            entities: A list of Entities.

        """
        similar_entities = []
        for e in entities:
            # Don't return the artists given in the
            # parms (for the case where there are
            # multiple artists and they are related
            # to each other).
            similar_entities += [
                ent
                for ent
                in self.kb_api.get_related_entities(e)
                if ent not in entities
            ]

        return similar_entities

    def _query_songs_by_artist(self, entities: List[str]):
        """Unary Command

        Returns a list of Artists for
        all Entities in the parameters.

        Args:
            entities: A list of Entities.

        """
        artists = []
        for e in entities:
            artists += self.kb_api.get_songs_by_artist(e)

        return artists

    def _query_artist_by_song(self, entities: List[str]):
        """Unary Command

        Returns a list of Artists for
        all Entities in the parameters.

        Args:
            entities: A list of Entities.

        """
        artists = []
        for e in entities:
            artists += [
                song.get('artist_name')
                for song
                in self.kb_api.get_song_data(e)
            ]

        return artists

    def _evaluate(self, tree: nltk.tree.Tree):
        """This function will evaluate the parse tree
        generated by the NLP layer.  It recursively
        evaluates the tree from the top down.  The
        tree starts with a `terminal command` (ie play)
        at the root.  The tree's leaves of the tree are
        composed of `entities`, and the inner nodes are
        composed of operations on those entities.  This
        function evaluates the operations and entities
        into a single result, which is then given to the
        `terminal command` to act upon.

        """
        if tree.label() == "Root":
            func = self._evaluate(tree[0])
            result = self._evaluate(tree[1])
            func(result)
            return
        elif tree.label() == "Result":
            if tree[0].label() == "Entity":
                return self._evaluate(tree[0])
            if tree[0].label() == "Unary_Command":
                func = self._evaluate(tree[0])
                result = self._evaluate(tree[1])
                return func(result)
            if tree[1].label() == "Binary_Command":
                result_left = self._evaluate(tree[0])
                func = self._evaluate(tree[1])
                result_right = self._evaluate(tree[2])
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
              "evaluateEngine#self._evaluate",
              file=sys.stderr)
