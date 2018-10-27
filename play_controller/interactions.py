from typing import List

from knowledge_base.api import KnowledgeBaseAPI


class Interactions:
    def __init__(self, db_path):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    @property
    def intents(self):
        return {
            'control_play': (['start', 'play'], self.control_play),
            'control_stop': (['stop'], self.control_stop),
            'control_pause': (['pause'], self.control_pause),
            'control_forward': (['skip', 'next'], self.control_forward),
            'query_artist': (['who', 'artist'], self.query_artist),
            'query_similar_entities': (['like', 'similar'], self.query_similar_entities),
            'default': ([''], self.default),
        }

    @property
    def keywords(self):
        return {k: v[0] for k, v in self.intents.items()}

    @property
    def actions(self):
        return {k: v[1] for k, v in self.intents.items()}

    def control_play(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        if subjects:
            """
            TODO: 
                - query db for entity
                    - if it's of type song, play it
                    - if it's anything else, get the songs associated with 
                      it and play in DESC order
            """
            return 'Playing {}'.format(', '.join(subjects))
        elif remaining_text:
            return "Sorry, I don't understand"
        else:
            return 'Resume playing current song'

    def control_stop(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def control_pause(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def control_forward(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def query_artist(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def query_similar_entities(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def default(self, subjects: List[str] = None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'
