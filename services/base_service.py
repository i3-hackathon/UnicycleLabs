import datetime

import geo
from models import all_models
from models import model_base

class VehicleRequest(model_base.Model):
    location = model_base.ModelField('location', all_models.LatLng)
    start_time = model_base.DateTimeField('start_time')
    end_time = model_base.DateTimeField('end_time')

    @property
    def duration_minutes(self):
        delta = self.end_time - self.start_time
        return delta.seconds / 60    

class VehicleService(object):
    def get_vehicles(self, vehicle_request):
        return []

    def compute_distance(self, vehicle_request, car_lat, car_lng):
        return geo.earth_distance_meters(
            vehicle_request.location.lat, vehicle_request.location.lng,
            car_lat, car_lng)
