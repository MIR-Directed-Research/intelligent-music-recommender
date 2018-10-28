from collections import OrderedDict
from typing import List

from knowledge_base.api import KnowledgeBaseAPI


class Interactions:
    def __init__(self, db_path, player_controller):
        self.player = player_controller
        self.DB_path = db_path
        self.kb_api = KnowledgeBaseAPI(self.DB_path)

    def __call__(self,
                 subjects: List[str] = None,
                 commands: List[str] = None,
                 remaining_text: str = None,
                 ):
        """Initiates a chain-of-commands to act on the subject parameters.

        Args:
            subjects: List of subjects in the database.
            commands: Names of commands to enact.
            remaining_text: Any remaining text not parsed by the NLP layer.

        Returns:

        """
        # Sort the commands by precedence.
        sorted_commands = []
        for c in self.command_precedence:
            if c in commands:
                sorted_commands.append(c)

        # Call the highest precedence command.
        return self._next_operation(subjects=subjects,
                                    commands=commands,
                                    remaining_text=remaining_text,
                                    )

    @property
    def intents(self):
        """Returns mapping of `intentions`, their corresponding `signifiers`,
        and function handlers.

        The ordering of these commands matters, as it is used to
        store the precedence of operations.

        Returns (OrderedDict): Mappings of intentions, signifiers, and
            handlers.

        """
        return OrderedDict([
            ('control_play', (['start', 'play'], self._control_play)),
            ('control_stop', (['stop'], self._control_stop)),
            ('control_pause', (['pause'], self._control_pause)),
            ('control_forward', (['skip', 'next'], self._control_forward)),
            ('query_artist', (['who', 'artist'], self._query_artist)),
            ('query_similar_entities', (['like', 'similar'], self._query_similar_entities)),
            ('default', ([''], self._default)),
        ])

    @property
    def keywords(self):
        return {k: v[0] for k, v in self.intents.items()}

    @property
    def actions(self):
        return {k: v[1] for k, v in self.intents.items()}

    @property
    def command_precedence(self):
        return [k for k, v in self.intents.items()]

    def _control_play(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      ):
        """Terminal command. Plays the subjects specified.

       TODO:
           - query db for entity
               - if it's of type song, play it
               - if it's anything else, get the songs associated with
                 it and play in DESC order

        """
        if subjects:

            self.player.play(subjects)
        elif remaining_text:
            self.player.respond("Sorry, I don't understand")
        else:
            self.player.respond('Resume playing current song')

    def _control_stop(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      ):
        # TODO: implement
        return 'Not implemented'

    def _control_pause(self,
                       subjects: List[str] = None,
                       commands: List[str] = None,
                       remaining_text: str = None,
                       ):
        # TODO: implement
        return 'Not implemented'

    def _control_forward(self,
                         subjects: List[str] = None,
                         commands: List[str] = None,
                         remaining_text: str = None,
                         ):
        # TODO: implement
        return 'Not implemented'

    def _query_artist(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      ):
        # TODO: implement
        return 'Not implemented'

    def _query_similar_entities(self,
                                subjects: List[str] = None,
                                commands: List[str] = None,
                                remaining_text: str = None,
                                ):
        # TODO: implement
        return 'Not implemented'

    def _default(self,
                 subjects: List[str] = None,
                 commands: List[str] = None,
                 remaining_text: str = None,
                 ):
        # TODO: implement
        return 'Not implemented'

    def _next_operation(self,
                        subjects: List[str] = None,
                        commands: List[str] = None,
                        remaining_text: str = None,
                        ):
        """Calls the next function in the commands parameter.

        Args:
            subjects:
            commands:
            remaining_text:

        Returns:

        """
        next_command_name = commands.pop(0)
        next_func = self.actions.get(next_command_name, self._default)
        next_func(subjects=subjects,
                  commands=commands,
                  remaining_text=remaining_text,
                  )
