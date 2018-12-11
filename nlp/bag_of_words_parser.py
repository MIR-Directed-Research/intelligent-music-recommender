import re

import nltk
from nltk.corpus import stopwords

from knowledge_base.api import KnowledgeBaseAPI


class BOWParser:
    """
    This layer stores the NLP specific tooling and logic.

    References:
        https://stackoverflow.com/questions/42322902/how-to-get-parse-tree-using-python-nltk
        https://www.nltk.org/book/ch08.html
    """
    extra_stopwords = {'s', 'hey', 'want', 'you'}

    def __init__(self, db_path, keywords):
        # Download the stopwords if necessary.
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        self.unary_commands = keywords.get("unary")
        self.kb_api = KnowledgeBaseAPI(db_path)
        self.db_nouns = self.kb_api.get_all_music_entities()

    def _get_stop_words(self):
        # Remove all keywords from stopwords
        stop_words = set(stopwords.words('english'))
        stop_words |= BOWParser.extra_stopwords
        for _, words in self.unary_commands.items():
            for word in words:
                try:
                    stop_words.remove(word)
                except:
                    pass
        return stop_words

    def _gen_patterns(self):
        # Generate RegEx patterns from keywords
        patterns = {}
        for intent, keys in self.unary_commands.items():
            patterns[intent] = re.compile(r'\b'+r'\b|\b'.join(keys)+r'\b')
        return patterns

    def __call__(self, msg: str):
        # Identify the first subject from the database that matches.
        subjects = []
        for noun in self.db_nouns:
            if noun.lower() in msg.lower():
                pattern = re.compile(noun, re.IGNORECASE)
                msg = pattern.sub('', msg)
                subjects.append(noun.strip())

        # Remove punctuation from the string
        msg = re.sub(r"[,.;@#?!&$']+\ *",
                     " ",
                     msg,
                     flags=re.VERBOSE)

        # Clean the stopwords from the input.
        stop_words = self._get_stop_words()
        clean_msg = ' '.join([word for word in msg.lower().split(' ')
                              if word not in stop_words])

        # Parse the keywords from the filtered input.
        patterns = self._gen_patterns()
        intents = []
        for intent, pattern in patterns.items():
            sub_msg = re.sub(pattern, '', clean_msg)
            if sub_msg != clean_msg:
                intents.append(intent)
                clean_msg = sub_msg

        remaining_text = clean_msg.strip()
        return intents, subjects, remaining_text
