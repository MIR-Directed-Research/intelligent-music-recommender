import re
from functools import lru_cache
from typing import List

import nltk

from knowledge_base.api import KnowledgeBaseAPI


class TreeParser:
    """
    This class contains tree-parsing logic that will convert
    input text to an NLTK Parse-Tree using a Context Free
    Grammar.

    References:
        https://stackoverflow.com/questions/42322902/how-to-get-parse-tree-using-python-nltk
        https://www.nltk.org/book/ch08.html

    """

    def __init__(self, db_path, keywords):
        self.keywords = keywords
        self.kb_api = KnowledgeBaseAPI(db_path)
        self.kb_named_entities = self.kb_api.get_all_music_entities()

    def __call__(self, msg: str):
        """Creates an NLTK Parse Tree from the user input msg.

        Args:
            msg: A string of user input.
                 i.e 'play something similar to Justin Bieber'

        Returns: An NLTK parse tree, as defined by the CFG given
                 in the "parser" function.

        """
        # Remove punctuation from the string
        msg = re.sub(r"[.?']+\ *",
                     " ",
                     msg,
                     flags=re.VERBOSE)

        # Parse sentence into list of tokens containing
        #  only entities and commands.
        tokens = self._lexer(msg)

        # Generate an NLTK parse tree
        tree = self._parser(tokens)
        return tree

    @property
    @lru_cache(1)
    def _unary_command_regexes(self):
        """Generates RegEx patterns from command signifiers.

        """
        patterns = {}
        for intent, keys in self.keywords.get("unary").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    @property
    @lru_cache(1)
    def _terminal_command_regexes(self):
        """Generates RegEx patterns from command signifiers.

        """
        patterns = {}
        for intent, keys in self.keywords.get("terminal").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    @property
    @lru_cache(1)
    def _binary_command_regexes(self):
        """Generates RegEx patterns from command signifiers.

        """
        patterns = {}
        for intent, keys in self.keywords.get("binary").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    def _lexer(self, msg: str):
        """Lexes an input string into a list of tokens.

        This lexer first looks for Entities in the input string
        and parses them into tokens of the same name
        (i.e. 'blah U2 blah' -> ['U2']).

        Next, the lexer will look for Commands by searching for
        keywords that signify the command. These keyword+command
        pairings are defined in the command_evaluation layer.

        Args:
            msg: A string of user input.
                 i.e 'play something similar to justin bieber'

        Returns: A tokenized list of commands and Entities.
            i.e. ['control_play', 'query_similar_entities', 'Justin Bieber']

        """

        def lexing_algorithm(text):
            # TODO: >= O(n^2) (horrible time complexity). In the interest of
            # making forward progress, optimize this later.  Could use a
            # bloom filter to look for matches, then binary search  on
            # entities/commands find specific match once possible match is
            # found.  Or even just use a hashmap for searching.

            # Base case.
            if text == "":
                return []

            # 1. Parse named entities.
            for entity in self.kb_named_entities:
                if entity.lower() in text.lower():
                    pieces = text.lower().split(entity.lower())
                    left = pieces[0]
                    right = pieces[1]
                    if left == text or right == text:
                        # Safety measure to prevent '' causing infinite recursion.
                        break
                    return lexing_algorithm(left) + [entity.strip()] + lexing_algorithm(right)

            # 2. Parse unary commands.
            for intent, pattern in self._unary_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return lexing_algorithm(left) \
                           + [intent] \
                           + lexing_algorithm(right)

            # 3. Parse terminal commands.
            for intent, pattern in self._terminal_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return lexing_algorithm(left) \
                           + [intent] \
                           + lexing_algorithm(right)

            # 4. Parse binary commands.
            for intent, pattern in self._binary_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return lexing_algorithm(left) \
                           + [intent] \
                           + lexing_algorithm(right)

            # If no matches, then the word is a stopword.
            return []

        return lexing_algorithm(msg)

    def _parser(self, tokens: List[str]):
        """Generates a Parse Tree from a list of tokens
        provided by the Lexer.

        Args:
            tokens: A tokenized list of commands and Entities.
            i.e. ['control_play', 'query_similar_entities', 'Justin Bieber']

        Returns: An nltk parse tree, as defined by the CFG given
                 in this function.

        """

        # TODO:   Improve the CFG work for the following:
        #          -  Play songs faster than despicito
        #          -  Play something similar to despicito but faster
        #          -  Play something similar to u2 and justin bieber

        def gen_lexing_patterns(vals: List[str]):
            # TODO: Here we remove entries containing ',
            #       as it is a special character used by
            #       the NLTK parser. We need to fix this
            #       eventually.
            safe_vals = [s for s in vals if "\'" not in s]
            return "' | '".join(safe_vals) or "NONE"

        # A Probabilistic Context Free Grammar (PCFG)
        # can be used to simulate "operator precedence",
        # which removes the problems of ambiguity in
        # the grammar.
        grammar = nltk.PCFG.fromstring("""
        Root -> Terminal_Command Result         [0.6]
        Root -> Terminal_Command                [0.4]
        Result -> Entity                        [0.5]
        Result -> Unary_Command Result          [0.1]
        Result -> Result Binary_Command Result  [0.4]
        Entity -> '{}'                          [1.0]
        Unary_Command -> '{}'                   [1.0]
        Terminal_Command -> '{}'                [1.0]
        Binary_Command -> '{}'                  [1.0]
        """.format(
            gen_lexing_patterns(self.kb_named_entities),
            gen_lexing_patterns(self.keywords.get("unary").keys()),
            gen_lexing_patterns(self.keywords.get("terminal").keys()),
            gen_lexing_patterns(self.keywords.get("binary").keys()),
        ))

        parser = nltk.ViterbiParser(grammar)
        # TODO: Returns the first tree, but need to deal with
        #       case where grammar is ambiguous, and more than
        #       one tree is returned.
        return next(parser.parse(tokens))
