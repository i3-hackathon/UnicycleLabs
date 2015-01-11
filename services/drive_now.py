import requests

from models import all_models
from services import base_service

class DriveNowService(base_service.VehicleService):
    def get_vehicles(self, vehicle_request):
        url = 'https://api2.drive-now.com/cities'
        params = {
            'expandNearestCity': 1,
            'onlyCarsNotInParkingSpace': 1,
            'latitude': vehicle_request.location.lat,
            'longitude': vehicle_request.location.lng,
            'expand': 'full',
            }
        session = requests.Session()
        session.headers.update({
            'X-Api-Key': 'adf51226795afbc4e7575ccc124face7'
            })
        response = session.get(url, params=params)
        nearest_city = response.json()['items'][0]
        vehicles = self.make_vehicles(vehicle_request, nearest_city['cars']['items'])
        return [v for v in vehicles if v.distance_meters < 8000]

    def make_vehicles(self, vehicle_request, cars):
        vehicles = []
        for car in cars:
            vehicles.append(all_models.Vehicle({
                'service': all_models.Service.DRIVE_NOW,
                'price_total': self.compute_price(vehicle_request),
                'price_details': '$12 for the first 30 mins, $0.32/minute after',
                'location': {
                    'lat': car['latitude'],
                    'lng': car['longitude'],
                    },
                'distance_meters': self.compute_distance(vehicle_request, car['latitude'], car['longitude']),
                'address': ' '.join(car['address']),
                'license_plate': car['licensePlate'],
                'make': car['make'],
                'model': car['modelName'].replace('BMW', '').strip(),
                'color': car['color'],
                'vehicle_name': car['name'],
                'image_url': 'https://us.drive-now.com/static/drivenow/img/cars/%s.png' % car['modelIdentifier'],
                'service_logo_url': 'drivenow-logo.png',
                'map_icon_url': 'drivenow-map-logo.png'
                }))
        return vehicles

    def compute_price(self, vehicle_request):
        duration = vehicle_request.duration_minutes
        return 12 + max(duration - 30, 0) * 0.32

if __name__ == '__main__':
    request = base_service.VehicleRequest({
        'start_time': u'2015-01-10T23:00:00Z',
        'end_time': u'2015-01-11T01:00:00Z',
        'location': {
            'lat': 37.7735937,
            'lng': -122.4036157,
            }        
        })
    print DriveNowService().get_vehicles(request)
