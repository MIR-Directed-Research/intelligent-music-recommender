import re
from functools import lru_cache

import nltk

from knowledge_base.api import KnowledgeBaseAPI


class TreeParser:
    """
    This class contains tree parsing logic that will convert
    input text to a Parse-Tree using a Context Free Grammar.

    References:
        https://stackoverflow.com/questions/42322902/how-to-get-parse-tree-using-python-nltk
        https://www.nltk.org/book/ch08.html
    """

    def __init__(self, db_path, keywords):
        self.keywords = keywords
        self.kb_api = KnowledgeBaseAPI(db_path)
        self.kb_named_entities = self.kb_api.get_all_music_entities()

    @property
    @lru_cache(1)
    def _unary_command_regexes(self):
        # Generate RegEx patterns from command signifiers.
        patterns = {}
        for intent, keys in self.keywords.get("unary").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    @property
    @lru_cache(1)
    def _terminal_command_regexes(self):
        # Generate RegEx patterns from command signifiers.
        patterns = {}
        for intent, keys in self.keywords.get("terminal").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    @property
    @lru_cache(1)
    def _binary_command_regexes(self):
        # Generate RegEx patterns from command signifiers.
        patterns = {}
        for intent, keys in self.keywords.get("binary").items():
            if keys:
                patterns[intent] = re.compile(r'\b' + r'\b|\b'.join(keys) + r'\b')
        return patterns

    def parse_entities_and_commands(self, msg):
        def algorithm(text):
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
                    pieces = text.split(entity.lower())
                    left = pieces[0]
                    right = pieces[1]
                    if left == text or right == text:
                        # Safety measure to prevent '' causing infinite recursion.
                        break
                    return algorithm(left) + [entity.strip()] + algorithm(right)

            # 2. Parse unary commands.
            for intent, pattern in self._unary_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return algorithm(left) + [intent] + algorithm(right)

            # 3. Parse terminal commands.
            for intent, pattern in self._terminal_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return algorithm(left) + [intent] + algorithm(right)

            # 4. Parse binary commands.
            for intent, pattern in self._binary_command_regexes.items():
                sub_msg = re.sub(pattern, 'MARKER', text)
                if sub_msg != text:
                    pieces = sub_msg.split('MARKER')
                    left = pieces[0]
                    right = pieces[1]
                    return algorithm(left) + [intent] + algorithm(right)

            # If no matches, then the word is a stopword.
            return []

        return algorithm(msg)

    def generate_parse_tree(self, tokens):
        """
        TODO: make the CFG work for the following:
            Play songs faster than despicito
            Play something similar to despicito but faster
            Play something similar to u2 and justin bieber

        """
        grammar = nltk.CFG.fromstring("""
        Root -> Terminal_Command Result
        Result -> Entity
        Result -> Unary_Command Result
        Result -> Result Binary_Command Result
        Entity -> '{}'
        Unary_Command -> '{}'
        Terminal_Command -> '{}'
        Binary_Command -> '{}' 
        """.format(
            "' | '".join(self.kb_named_entities),
            "' | '".join(self.keywords.get("unary").keys()),
            "' | '".join(self.keywords.get("terminal").keys()),
            "' | '".join(self.keywords.get("binary").keys()),
        ))

        parser = nltk.ChartParser(grammar)
        # TODO: Returns the first tree, but need to deal with
        #       case where grammar is ambiguous, and more than
        #       one tree is returned.
        return next(parser.parse(tokens))

    def __call__(self, msg: str):
        # Remove punctuation from the string
        msg = re.sub(r"[,.;@#?!&$']+\ *",
                     " ",
                     msg,
                     flags=re.VERBOSE)

        # Parse sentence into list of tokens containing
        #  only entities and commands.
        clean_tokens = self.parse_entities_and_commands(msg)

        # Generate an NLTK parse tree
        tree = self.generate_parse_tree(clean_tokens)
        return tree
