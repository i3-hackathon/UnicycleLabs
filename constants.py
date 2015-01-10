import os

PROJECTPATH = os.environ.get('PROJECTPATH')

DEBUG = False

APP_LOG_FILENAME = os.path.join(PROJECTPATH, 'app.log')

try:
    from constants_override import *
except ImportError:
    pass
