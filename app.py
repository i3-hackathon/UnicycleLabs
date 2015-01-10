from flask import json
from flask import render_template
from flask import request

from app_core import app
import constants
from models import all_models
from services import base_service
from services import drive_now

class Status(object):
    OK = 'OK'

@app.route('/')
def index():
    return render_template('index.html')

VEHICLE_SERVICES = (drive_now.DriveNowService(),)

@app.route('/search')
def search():
    lat = request.args['lat']
    lng = request.args['lng']
    vehicle_request = base_service.VehicleRequest({
        'duration_minutes': int(request.args['duration']),
        'location': {
            'lat': request.args['lat'],
            'lng': request.args['lng'],
            }
        })

    vehicles = []
    for service in VEHICLE_SERVICES:
        vehicles.extend(service.get_vehicles(vehicle_request))
    raw_vehicles = [v.raw for v in vehicles]
    return json.jsonify(status=Status.OK, vehicles=raw_vehicles)

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
