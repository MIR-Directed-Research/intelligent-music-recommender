from time import sleep


class DummyController:
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
