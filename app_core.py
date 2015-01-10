from flask import Flask

import constants

class MyFlask(Flask):
    def get_send_file_max_age(self, name):
        if name.startswith('js/') or name.startswith('css/'):
            return 0
        return super(MyFlask, self).get_send_file_max_age(name)

class AppConfig(object):
    pass

app = MyFlask(__name__)
app.config.from_object(__name__ + '.AppConfig')

if not constants.DEBUG:
    import logging
    file_handler = logging.FileHandler(constants.APP_LOG_FILENAME)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
