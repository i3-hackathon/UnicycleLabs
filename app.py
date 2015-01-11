import datetime
import os

from dateutil import parser as dateutil_parser
from flask import json
from flask import render_template
from flask import request

from app_core import app
import constants
from historical import drive_now_historical
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
    vehicles = utils.flatten(vehicles_lists)
    return sorted(vehicles, key=lambda v: v.distance_meters)

@app.route('/historical')
def historical():
    return render_template('historical.html')

@app.route('/historical/search')
def historical_search():
    index = drive_now_historical.Index()
    latlngs = index.get_latlngs(request.args['day'], request.args['hour'])
    dt = datetime.datetime(year=2014, month=10, day=int(request.args['day']), hour=int(request.args['hour']))
    return json.jsonify(latlngs=latlngs, date_str=dt.strftime('%a %b %d'), time_str=dt.strftime('%I%p').lower())

if __name__ == '__main__':
    app.debug = constants.DEBUG
    app.run()
