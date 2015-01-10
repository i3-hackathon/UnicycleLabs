from flask import render_template

from app_core import app
import constants

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
