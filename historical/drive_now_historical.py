import json
import os

import constants

class Index(object):
    index = None

    @staticmethod
    def get_index():
        if not Index.index:
            Index.index = json.load(open(os.path.join(
                constants.PROJECTPATH, 'data/munich_october_pickups_by_hour_index.json')))
        return Index.index

    def get_latlngs(self, day_of_month, hour_of_day):
        index = self.get_index()
        return index.get(str(day_of_month), {}).get(str(hour_of_day), [])
