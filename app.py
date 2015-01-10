from flask import json
from flask import render_template
from flask import request

from app_core import app
import constants
from models import all_models
from services import base_service
from services import drive_now
from services import getaround
from services import zipcar
import utils

class Status(object):
    OK = 'OK'

@app.route('/')
def index():
    return render_template('index.html')

VEHICLE_SERVICES = (drive_now.DriveNowService(), zipcar.ZipcarService(), getaround.GetaroundService())

@app.route('/search')
def search():
    vehicle_request = base_service.VehicleRequest({
        'start_time': request.args['start_time'],
        'end_time': request.args['end_time'],
        'location': {
            'lat': float(request.args['lat']),
            'lng': float(request.args['lng'])   ,
            }
        })
    vehicles = get_vehicles(vehicle_request)
    raw_vehicles = [v.raw for v in vehicles]
    return json.jsonify(status=Status.OK, vehicles=raw_vehicles)

def get_vehicles(vehicle_request):
    fns = []
    import pprint
    for service in VEHICLE_SERVICES:
        fns.append(lambda service=service: service.get_vehicles(vehicle_request))
    vehicles_lists = utils.parallelize_closures(fns)
    return utils.flatten(vehicles_lists)

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
