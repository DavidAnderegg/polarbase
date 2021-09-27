import os
import json
import jsonschema
import numpy as np
from jsonschema.exceptions import ValidationError

class ObjectNotFound(Exception):
    pass

class InitJsonNotValid(Exception):
    pass


class Polar(object):

    def __init__(self, polar_dict):
        self.polar_dict = polar_dict

    def __getattr__(self, attr) -> np.float_:
        if attr in self.polar_dict.keys():
            return self.polar_dict[attr]
        else:
            raise(AttributeError(f'"{attr}" could not be found'))

    def __len__(self):
        return len(self.polar_dict)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self.polar_dict.keys())) + ']'


class Object(object):
    init_json_scheme = None

    def __init__(self, path):
        self.init_json = dict()

        # If the directory does not exist, throw an error
        if not os.path.exists(path):
            raise(ObjectNotFound(f'{path} does not exist'))

        # If a 'init.json' can be loaded, do it
        # the ability to load it is indicated by self.init_json_scheme not
        # beeing None
        if self.init_json_scheme is not None:
            self._load_init_json(path)

        # load the object itself
        self.load(path)

    def _load_init_json(self, path):
        # This function loads the 'init.json' and validates it against
        # 'init_json_schema'

        json_path = os.path.join(path, 'init.json')

        try:
            with open(json_path) as f:
                json_string = f.read()
        except FileNotFoundError:
            json_string = '{}'

        try:
            json_object = json.loads(json_string)
        except json.JSONDecodeError as exc:
            raise(InitJsonNotValid(f'The "init.json" file in "{path:s}" is not ' \
                    'valid')) from exc

        try:
            jsonschema.validate(instance=json_object,
                    schema=self.init_json_scheme)
        except ValidationError as exc:
            raise(InitJsonNotValid(f'The "init.json" file in "{path:s}" is not ' \
                    'valid')) from exc

        self.init_json = json_object


    def load(self, path):
        # this is the load function itself. It has to be subclassed
        raise(NotImplementedError(f'{type(self)} has not implemented the ' \
        'function "load"'))



class ObjectList(Object):
    list_type = Object

    def __init__(self, path):
        self.container = dict()
        super().__init__(path)

    def __getattr__(self, attr) -> list_type:
        if attr in self.container.keys():
            return self.container[attr]
        else:
            raise(AttributeError(f'"{attr}" could not be found'))

    def __len__(self):
        return len(self.container)

    def __str__(self) -> str:
        return '[' + ', '.join(map(str, self.container.keys())) + ']'

    def load(self, path):
        for folder in os.listdir(path):
            self.container[folder] = self.list_type(os.path.join(path, folder))
