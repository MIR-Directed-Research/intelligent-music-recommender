from collections import OrderedDict
from typing import List

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

    def __call__(self,
                 subjects: List[str] = None,
                 commands: List[str] = None,
                 remaining_text: str = None,
                 ):
        """Initiates a sequence of commands that will act
        on the subject parameters in order of command
        precedence.

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
        self._next_operation(subjects=subjects,
                             commands=sorted_commands,
                             remaining_text=remaining_text,
                             )

    @property
    def intents(self):
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
            ('query_commands', (['hi', 'how', 'hello'], self._query_commands)),
            ('control_stop', (['stop'], self._control_stop)),
            ('control_pause', (['pause'], self._control_pause)),
            ('control_forward', (['skip', 'next'], self._control_skip)),
            ('query_similar_entities', (['like', 'similar'], self._query_similar_entities)),
            ('control_play', (['start', 'play'], self._control_play)),
            ('query_artist', (['who', 'artist'], self._query_artist)),
            ('default', ([], self._default)),
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
                k: v[0] for k, v in self.intents.items()
            },
            "binary": {
                k: v[0] for k, v in self.binary_commands.items()
            },
        }

    @property
    def actions(self):
        return {k: v[1] for k, v in self.intents.items()}

    @property
    def command_precedence(self):
        return [k for k, v in self.intents.items()]

    def _query_commands(self,
                        subjects: List[str] = None,
                        commands: List[str] = None,
                        remaining_text: str = None,
                        response_msg: str = None,
                        ):
        """Terminal command. Reports on possible commands and interactions.

        """
        if subjects:
            # Handle question about specific `subjects`.
            self.player.respond("I'm sorry, I can't answer that one")
        else:
            # Handle genery inquiries.
            self.player.respond("Hi there! Ask me to play artists or songs. "
                                "I can also find songs that are similar to other "
                                "artists.")

    def _control_play(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      response_msg: str = None,
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
            self.player.respond("I'm sorry, I couldn't find that for you.")
        else:
            self.player.respond('Resuming the current song')

    def _control_stop(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      response_msg: str = None,
                      ):
        self.player.stop(subjects)

    def _control_pause(self,
                       subjects: List[str] = None,
                       commands: List[str] = None,
                       remaining_text: str = None,
                       response_msg: str = None,
                       ):
        self.player.pause(subjects)

    def _control_skip(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      response_msg: str = None,
                      ):
        # TODO: Add number parsing for "skip forward 2 songs".
        self.player.skip(subjects)

    def _control_intersection(self,
                              subjects: List[str] = None,
                              commands: List[str] = None,
                              remaining_text: str = None,
                              response_msg: str = None,
                              ):
        # TODO
        self.player.skip(subjects)

    def _control_union(self,
                       subjects: List[str] = None,
                       commands: List[str] = None,
                       remaining_text: str = None,
                       response_msg: str = None,
                       ):
        # TODO
        self.player.skip(subjects)

    def _query_artist(self,
                      subjects: List[str] = None,
                      commands: List[str] = None,
                      remaining_text: str = None,
                      response_msg: str = None,
                      ):
        # TODO: implement for fetching current state, ie "who is this artist?"
        self.player.respond(subjects)

    def _query_similar_entities(self,
                                subjects: List[str] = None,
                                commands: List[str] = None,
                                remaining_text: str = None,
                                response_msg: str = None,
                                ):
        similar_entities = []
        for e in subjects:
            similar_entities += self.kb_api.get_related_entities(e)

        if not similar_entities:
            self.player.respond("I'm sorry, I couldn't find that for you.")
        else:
            self._next_operation(subjects=similar_entities,
                                 commands=commands,
                                 remaining_text=remaining_text,
                                 response_msg=response_msg,
                                 )

    def _default(self,
                 subjects: List[str] = None,
                 commands: List[str] = None,
                 remaining_text: str = None,
                 response_msg: str = None,
                 ):
        self.player.respond("I'm sorry, I don't understand.")

    def _next_operation(self,
                        subjects: List[str] = None,
                        commands: List[str] = None,
                        remaining_text: str = None,
                        response_msg: str = None,
                        ):
        """Calls the next function in the commands parameter.

        """
        next_command_name = commands.pop(0) if commands else self._default
        next_func = self.actions.get(next_command_name, self._default)
        next_func(subjects=subjects,
                  commands=commands,
                  remaining_text=remaining_text,
                  response_msg=response_msg,
                  )
