import os
import copy
import json
import jsonschema
import numpy as np
from jsonschema.exceptions import ValidationError


class ObjectNotFound(Exception):
    pass


class InitJsonNotValid(Exception):
    pass


class Polar(object):

    def __init__(self, polar_dict, parent):
        self.parent = parent

        # check if everything is a numpy array
        for key in polar_dict.keys():
            if not isinstance(polar_dict[key], np.ndarray):
                raise ValueError(f'{key} is not a np.ndarray')

        self.polar_dict = polar_dict

    def __getitem__(self, key) -> np.ndarray:
        return self.polar_dict[key]

    def __len__(self):
        return len(self.polar_dict)

    def __str__(self) -> str:
        return '["' + '", "'.join(map(str, self.polar_dict.keys())) + '"]'

    def between(self, min_val, max_val, filter_key):
        # this returns itself, but only with values min_val <= x <= max_val
        indices = np.where(np.logical_and(self.polar_dict[filter_key] >=
                           min_val, self.polar_dict[filter_key] <= max_val))
        new = copy.deepcopy(self)
        new.polar_dict = {k:
                          new.polar_dict[k][indices]
                          for k in new.polar_dict.keys()}
        return new


class Object(object):
    init_json_scheme = None

    def __init__(self, path, parent):
        self.parent = parent
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
            raise(InitJsonNotValid(f'The "init.json" file in "{path:s}" is not'
                                   'valid')) from exc

        try:
            jsonschema.validate(instance=json_object,
                                schema=self.init_json_scheme)
        except ValidationError as exc:
            raise(InitJsonNotValid(f'The "init.json" file in "{path:s}" is not'
                                   'valid')) from exc

        self.init_json = json_object

    def load(self, path):
        # this is the load function itself. It has to be subclassed
        raise(NotImplementedError(f'{type(self)} has not implemented the '
                                  'function "load"'))


class ObjectList(Object):
    list_type = Object

    def __init__(self, path, parent):
        self.container = dict()
        super().__init__(path, parent)

    def __getitem__(self, key):
        return self.container[key]

    def __len__(self):
        return len(self.container)

    def __str__(self) -> str:
        return '["' + '", "'.join(map(str, self.container.keys())) + '"]'

    def load(self, path):
        for folder in os.listdir(path):
            self.container[folder] = self.list_type(os.path.join(path, folder),
                                                    self)

    def plot(self, x, y, axes=None):
        for item in self.container.values():
            item.plot(x, y, axes)

    def between(self, min_val, max_val, filter_key):
        result = copy.deepcopy(self)
        for key in result.container.keys():
            result.container[key] = result.container[key].between(min_val,
                                                                  max_val,
                                                                  filter_key)
        return result
