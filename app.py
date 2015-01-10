from flask import json
from flask import render_template

from app_core import app
import constants
from models import all_models

class Status(object):
    OK = 'OK'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    vehicles = [
        all_models.Vehicle.new(
            service=all_models.Service.DRIVE_NOW,
            price_hourly=13.25,
            location=all_models.LatLng.new(lat=37.7762739, lng=-122.4073876),
            image_url='https://us.drive-now.com/static/drivenow/img/cars/bmw_activee.png')
        ]
    raw_vehicles = [v.raw for v in vehicles]
    return json.jsonify(status=Status.OK, vehicles=raw_vehicles)

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
