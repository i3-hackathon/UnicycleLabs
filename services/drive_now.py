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
        return self.make_vehicles(vehicle_request, nearest_city['cars']['items'])

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
                'address': ' '.join(car['address']),
                'license_plate': car['licensePlate'],
                'make': car['make'],
                'model': car['modelName'],
                'color': car['color'],
                'vehicle_name': car['name'],
                'image_url': 'https://us.drive-now.com/static/drivenow/img/cars/%s.png' % car['modelIdentifier'],
                }))
        return vehicles

    def compute_price(self, vehicle_request):
        duration = vehicle_request.duration_minutes
        return 12 + max(duration - 30, 0) * 0.32

if __name__ == '__main__':
    request = base_service.VehicleRequest({
        'location': {
            'lat': 37.7735937,
            'lng': -122.4036157,
            }        
        })
    print DriveNowService().get_vehicles(request)
