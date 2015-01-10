from app_core import app
import constants

@app.route('/')
def index():
    return 'Hello'

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
