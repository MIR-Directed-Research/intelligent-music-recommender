def control_play(entity):
    # TODO: implement
    return 'Not implemented'


def control_stop(entity):
    # TODO: implement
    return 'Not implemented'


def control_pause(entity):
    # TODO: implement
    return 'Not implemented'


def control_forward(entity):
    # TODO: implement
    return 'Not implemented'


def query_artist(entity):
    # TODO: implement
    return 'Not implemented'


def default(entity):
    # TODO: implement
    return 'Not implemented'


intentions = {
    'control_play': (['start', 'play '], control_play),
    'control_stop': (['stop'], control_stop),
    'control_pause': (['pause'], control_pause),
    'control_forward': (['skip', 'next'], control_forward),
    'query_artist': (['who', 'artist'], query_artist),
    'default': ([''], default),
}
keywords = {k: v[0] for k, v in intentions.items()}
actions = {k: v[1] for k, v in intentions.items()}
