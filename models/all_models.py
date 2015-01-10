from models import model_base

class Service(object):
    DRIVE_NOW = 'DRIVE_NOW'
    GETAROUND = 'GETAROUND'
    ZIPCAR = 'ZIPCAR'

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
    price_hourly = model_base.FloatField('price_hourly')
    location = model_base.ModelField('location', LatLng)
    image_url = model_base.StringField('image_url')
