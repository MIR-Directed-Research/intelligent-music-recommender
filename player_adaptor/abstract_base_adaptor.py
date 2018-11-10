from abc import abstractmethod


class AbstractBaseAdaptor:
    """An Abstract Base adaptor for defining the
    functionality of a player adaptor.

    """
    @abstractmethod
    def play(self, entity=None):
        pass

    @abstractmethod
    def pause(self, entity=None):
        pass

    @abstractmethod
    def stop(self, entity=None):
        pass

    @abstractmethod
    def skip(self, entity=None):
        pass

    @abstractmethod
    def respond(self, response=None):
        pass
