class MockController:
    """Mocks a player controller for testing.

    Allows a test to access the output the caller through
    exploiting pass-by-reference of the `state` dictionary.

    """

    def __init__(self, state: dict):
        self.state = state

    def play(self, entity=None):
        self.state['play'] = entity

    def pause(self, entity=None):
        self.state['pause'] = entity

    def stop(self, entity=None):
        self.state['stop'] = entity

    def skip(self, entity=None):
        self.state['skip'] = entity

    def respond(self, response=None):
        self.state['respond'] = response
