import datetime

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
    def get_vehicles(vehicle_request):
        return []
