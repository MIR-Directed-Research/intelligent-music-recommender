from time import sleep

from player_adaptor.abstract_base_adaptor import AbstractBaseAdaptor


class DummyController(AbstractBaseAdaptor):
    """A dummy player-controller for testing the system.

    This will eventually be replaced with a controller
    that calls the functions of a real player.

    """

    def __init__(self):
        self.sleep_time = 0.10

    def play(self, entity=None):
        sleep(self.sleep_time)
        print('Playing: {}'.format(entity))

    def pause(self, entity=None):
        sleep(self.sleep_time)
        print('Pausing: {}'.format(entity))

    def stop(self, entity=None):
        sleep(self.sleep_time)
        print('Stopping: {}'.format(entity))

    def skip(self, entity=None):
        sleep(self.sleep_time)
        print('Skipping: {}'.format(entity))

    def respond(self, response=None):
        sleep(self.sleep_time)
        print('Response: {}'.format(response))
