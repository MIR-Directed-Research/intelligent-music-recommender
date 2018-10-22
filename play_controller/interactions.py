from knowledge_base.api import KnowledgeBaseAPI


class Interactions:
    def __init__(self, db_path):
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    @property
    def intents(self):
        return {
            'control_play': (['start', 'play '], self.control_play),
            'control_stop': (['stop'], self.control_stop),
            'control_pause': (['pause'], self.control_pause),
            'control_forward': (['skip', 'next'], self.control_forward),
            'query_artist': (['who', 'artist'], self.query_artist),
            'default': ([''], self.default),
        }

    @property
    def keywords(self):
        return {k: v[0] for k, v in self.intents.items()}

    @property
    def actions(self):
        return {k: v[1] for k, v in self.intents.items()}

    def control_play(self, db_subject=None, remaining_text=None):
        # TODO: implement
        if db_subject:
            """
            TODO: 
                - query db for entity
                    - if it's of type song, play it
                    - if it's anything else, get the songs associated with 
                      it and play in DESC order                      
            """
            return 'Playing {}'.format(db_subject)
        elif remaining_text:
            return "Sorry, I don't understand"
        else:
            return 'Resume playing current song'

    def control_stop(self, db_subject=None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def control_pause(self, db_subject=None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def control_forward(self, db_subject=None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def query_artist(self, db_subject=None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'

    def default(self, db_subject=None, remaining_text=None):
        # TODO: implement
        return 'Not implemented'
