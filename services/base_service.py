from models import all_models
from models import model_base

class VehicleRequest(model_base.Model):
    location = model_base.ModelField('location', all_models.LatLng)
    duration_minutes = model_base.NumberField('duration_minutes')

class VehicleService(object):
    def get_vehicles(vehicle_request):
        return []
