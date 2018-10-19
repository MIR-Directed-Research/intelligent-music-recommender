import sys

sys.path.append('../')
from play_controller.controller import Controller

DB_PATH = '../tests/test.db'
controller = Controller(DB_PATH)
for text in sys.stdin:
    for result in controller(text):
        print('Result: {}'.format(result))
