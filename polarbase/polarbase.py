import os
import sys

from polarbase.objects import folder_names, ObjectNotFound

class PolarBase(object):
    def __init__(self, database_path):
        self._objects = dict()
        self.load_database(database_path)

    def __getattr__(self, attr):
        if attr in self._objects.keys():
            return self._objects[attr]
        else:
            raise ObjectNotFound(f'"{attr}" does not exist')

    def load_database(self, database_path):
        if not os.path.exists(database_path):
            raise IOError(f'"{database_path} could not be found.')

        self.database_path = database_path

        for folder in os.listdir(database_path):
            if folder in folder_names.keys():
                self._objects[folder] = folder_names[folder](
                        os.path.join(database_path, folder))






if __name__ == '__main__':
    pb = PolarBase('../example/data')
    print(pb.airfoils.n0021.name)
