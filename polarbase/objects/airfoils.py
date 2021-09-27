import os
from attr import NOTHING
import numpy as np

from .objects import Object, ObjectList, ObjectNotFound
from .aerodynamicpolar import PolarList


class AirfoilGeometry(Object):
    def _load(self, path):
        self.lower = np.array([])
        self.upper = np.array([])


class Airfoil(Object):
    init_json_scheme = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                    "description": {"type": "string"},
                    "comment": {"type": "string"},
                }
            }

    def load(self, path):
        self.name =         self.init_json.get('name')
        self.description =  self.init_json.get('description')
        self.comment =      self.init_json.get('comment')

        # self.geometry = AirfoilGeometry(os.path.join(path, 'geometry'))
        try:
            self.polars = PolarList(os.path.join(path, 'polars'))
        except ObjectNotFound:
            self.polars = None


class AirfoilList(ObjectList):
    list_type = Airfoil
