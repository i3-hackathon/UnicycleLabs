from models import model_base

class Service(object):
    DRIVE_NOW = 'DRIVE_NOW'
    GETAROUND = 'GETAROUND'
    ZIPCAR = 'ZIPCAR'

class FuelType(object):
    ELECTRIC = 'ELECTRIC'
    GAS = 'GAS'

class LatLng(model_base.Model):
    lat = model_base.FloatField('lat')
    lng = model_base.FloatField('lng')

    def as_string(self):
        return '%s,%s' % (self.lat, self.lng)

    @staticmethod
    def from_string(s):
        try:
            parts = s.split(',')
            return LatLng.new(lat=float(parts[0]), lng=float(parts[1]))
        except:
            return None

class Vehicle(model_base.Model):
    service = model_base.StringField('service')
    price_total = model_base.FloatField('price_total')
    price_details = model_base.StringField('price_details')
    location = model_base.ModelField('location', LatLng)
    distance_meters = model_base.FloatField('distance_meters')
    address = model_base.StringField('address')
    license_plate = model_base.StringField('license_plate')
    make = model_base.StringField('make')
    model = model_base.StringField('model')
    year = model_base.NumberField('year', optional=True)
    color = model_base.StringField('color')
    vehicle_name = model_base.StringField('vehicle_name', optional=True)
    image_url = model_base.StringField('image_url')
    map_icon_url = model_base.StringField('map_icon_url')
    service_logo_url = model_base.StringField('service_logo_url')
    fuel_level = model_base.FloatField('fuel_level', optional=True)
    fuel_type = model_base.StringField('fuel_type', optional=True)
