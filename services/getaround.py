import requests

from models import all_models
from services import base_service

class GetaroundService(base_service.VehicleService):
    def get_vehicles(self, vehicle_request):
        url = 'http://index.getaround.com/v1.0/search'
        params = {
            'sort': 'best',
            'user_lat': vehicle_request.location.lat,
            'user_lng': vehicle_request.location.lng,
            'start_time': vehicle_request.raw['start_time'],
            'end_time': vehicle_request.raw['end_time'],
            'instant': 1,
            'properties': 'car_id,latitude,longitude,make,model,year,car_photo,owner_id,owner_name,car_photo,instant_rental,price_hourly,distance,total_price,timezone',
            'page': 1,
            'page_size': 500,
            'page_sort': 'magic',
            }
        response = requests.get(url, params=params)
        print response.url
        return self.make_vehicles(vehicle_request, response.json()['cars'])

    def make_vehicles(self, vehicle_request, cars):
        vehicles = []
        for car in cars[:3]:
            vehicles.append(all_models.Vehicle({
                'service': all_models.Service.GETAROUND,
                'price_total': car['total_price'],
                'price_details': '$%s/hour' % car['price_hourly'],
                'location': {
                    'lat': car['latitude'],
                    'lng': car['longitude'],
                    },
                'make': car['make'],
                'model': car['model'],
                'year': int(car['year']),
                'image_url': car['car_photo'],
                }))
        return vehicles

if __name__ == '__main__':
    request = base_service.VehicleRequest({
        'start_time': u'2015-01-10T23:00:00Z',
        'end_time': u'2015-01-11T01:00:00Z',
        'location': {
            'lat': 37.7735937,
            'lng': -122.4036157,
            }        
        })
    print GetaroundService().get_vehicles(request)
