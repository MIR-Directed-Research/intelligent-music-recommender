"""
Run this script from within the /bin directory:

cd bin/
python3 cli
"""
import sys
from time import sleep

sys.path.append('../')
from play_controller.controller import Controller

DB_PATH = '../tests/test.db'
controller = Controller(DB_PATH)
for text in sys.stdin:
    for result in controller(text):
        sleep(0.05)
        print('Result: {}'.format(result))
