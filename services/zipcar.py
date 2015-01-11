import re

import requests

import geo
from models import all_models
from models import model_base
from services import base_service
import utils

VEHICLE_MODEL_ALT_TEXT_RE = re.compile('<img[^>]+alt="([^"]+)"')

class ZipcarLocation(model_base.Model):
    description = model_base.StringField('description')
    has_vans = model_base.StringField('hasVans')
    latitude = model_base.ParsedFloatField('latitude')
    location_id = model_base.ParsedIntegerField('locationId')
    longitude = model_base.ParsedFloatField('longitude')
    market_id = model_base.ParsedIntegerField('marketId')
    restrictedP = model_base.StringField('restrictedP')
    vehicle_count = model_base.ParsedIntegerField('vehicleCount')

class ZipcarService(base_service.VehicleService):
    def get_vehicles(self, vehicle_request):
        url = 'http://www.zipcar.com/api/drupal/1.0/locations'
        params = {
            'lat': vehicle_request.location.lat,
            'lon': vehicle_request.location.lng,
            'lat_delta': 0.09058445728426767,
            'lon_delta': 0.2378927001953125,
            'locale': 'en-US',
        }
        response = requests.get(url, params=params)
        locations = map(ZipcarLocation, response.json()['locations'])
        nearest_locations = self.find_nearest_locations(vehicle_request, locations)
        return self.expand_locations(vehicle_request, nearest_locations)

    def find_nearest_locations(self, vehicle_request, locations):
        req_lat = vehicle_request.location.lat
        req_lng = vehicle_request.location.lng
        nonempty_locations = [l for l in locations if l.vehicle_count >= 1]
        ordered_locations = sorted(nonempty_locations,
            key=lambda loc: geo.earth_distance_meters(req_lat, req_lng, loc.latitude, loc.longitude))
        return ordered_locations[:10]

    def expand_locations(self, vehicle_request, locations):
        fns = []
        for location in locations:
            fns.append(lambda location=location: self.expand_location(vehicle_request, location))
        vehicles_lists = utils.parallelize_closures(fns)
        return utils.flatten(vehicles_lists)

    def expand_location(self, vehicle_request, location):
        url = 'http://www.zipcar.com/api/drupal/1.0/location-vehicles'
        params = {'location_id': location.location_id, 'locale': 'en-US'}
        response = requests.get(url, params=params)
        vehicles = []
        for zipcar_vehicle in response.json()['locationVehicles']:
            vehicles.append(self.make_vehicle(vehicle_request, zipcar_vehicle,
                all_models.LatLng.new(lat=location.latitude, lng=location.longitude)))
        return vehicles

    def make_vehicle(self, vehicle_request, zipcar_vehicle, latlng):
        zv = zipcar_vehicle
        # TODO: paralleize this
        vehicle_details = self.get_vehicle_details(zv['vehicleId'])
        return all_models.Vehicle({
            'service': all_models.Service.ZIPCAR,
            'price_total': float(zv['hourlyCost']) * vehicle_request.duration_minutes / 60.,
            'price_details': '$%s/hour' % zv['hourlyCost'],
            'vehicle_name': zv['description'],
            'location': latlng.raw,
            'distance_meters': self.compute_distance(vehicle_request, latlng.lat, latlng.lng),
            'make': vehicle_details.get('make'),
            'model': vehicle_details.get('model'),
            'image_url': 'https://media.zipcar.com/images/model-image?model_id=%s' % zv['modelId'],
            'service_logo_url': 'zipcar-logo.png',
            'map_icon_url': 'zipcar-map-logo.png',
            })

    def get_vehicle_details(self, vehicle_id):
        url = 'http://www.zipcar.com/api/drupal/1.0/car-profile/sf/%s?locale=en-US' % vehicle_id
        html = requests.get(url).text
        match = VEHICLE_MODEL_ALT_TEXT_RE.search(html)
        make_model = match.group(1) if match else None
        return {
            'make': make_model.split(' ')[0],
            'model': ' '.join(make_model.split(' ')[1:])
        }


if __name__ == '__main__':
    request = base_service.VehicleRequest({
        'start_time': u'2015-01-10T23:00:00Z',
        'end_time': u'2015-01-11T01:00:00Z',
        'location': {
            'lat': 37.7735937,
            'lng': -122.4036157,
            }        
        })
    print ZipcarService().get_vehicles(request)
