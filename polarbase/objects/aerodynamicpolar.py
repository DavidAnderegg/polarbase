import os
import re

from polarbase.objects import Object, ObjectList, Polar
from polarbase.utils import str2number, str2value


class LoadPolarError(Exception):
    pass


class AerodynamicPolar(Polar):
    def __init__(self, polar_dict, name=None, solver=None, solver_options=None,
            description=None, comment=None):
        super().__init__(polar_dict)

        self.name = name
        self.solver = solver
        self.solver_options = solver_options
        self.description = description
        self.comment = comment

    def __str__(self) -> str:
        available_polars = super().__str__()
        string = f'AERODYNAMIC POLAR\n' \
                 f'Name: \t\t{self.name}\n' \
                 f'Solver:\t\t{self.solver}\n' \
                 f'Description:\t{self.description}\n' \
                 f'Comment: \t{self.comment}\n' \
                 f'Available data:\t{available_polars}\n'
        return string


def load_file(path, properties):
    """ This is just a dummy function for loading a specific polar"""
    return dict()

def load_adflow_utils(path, properties):
    """ This function loads polars that were written by the package
    "adflow_utils"

    Properties:
        group_by    string      This creates a new polar everytime a new
                                "string" is found
    """

    def find_aero_options(file_lines):
        """ finds the position of the aero options in the file """
        n_aero_start = -1
        n_aero_end = -1
        aero_maker_line = None
        for n in range(len(file_lines)):
            line = file_lines[n]

            if aero_maker_line is not None:
                if n > n_aero_start and line == aero_maker_line:
                    n_aero_end = n
                    break
                continue

            if "Aero Options" in line:
                n_aero_start = n + 2
                aero_maker_line = file_lines[n+1]
                continue

        len_label = 0
        if aero_maker_line is not None:
            len_label = len(aero_maker_line.split()[0])
        return n_aero_start, n_aero_end, len_label

    def read_aero_options(lines, len_label):
        # assemble each value
        value_pairs = list()
        for line in lines:
            line_clean = str(line).lstrip().rstrip()

            if line[:len_label] == ' '*len_label:
                value_pairs[-1] += ' ' + line_clean
            else:
                value_pairs.append(line_clean)

        # convert them to dict
        aero_options = dict()
        for value_pair in value_pairs:
            key = str(value_pair[:len_label]).strip()
            value = str2value(value_pair[len_label:])
            aero_options[key] = value

        return aero_options

    def find_results(file_lines):
        n_results_header = -1
        n_results_start = -1

        for n in range(len(file_lines)):
            line = file_lines[n]

            if "RESULTS" in line:
                n_results_header = n + 1
                n_results_start = n + 3
                break

        return n_results_header, n_results_start

    def read_results(result_lines, header_string):
        # get the keys for the dict
        header_string = ' '.join(header_string.split())
        keys = header_string.split()

        # split the data
        results = dict()
        for line in result_lines:
            line = ' '.join(line.split())
            items = line.split()

            for n in range(len(keys)):
                key = keys[n]
                item = str2number(items[n])

                if key in results:
                    results[key].append(item)
                else:
                    results[key] = [item]

        return results

    def find_group_by_splits(group_by_list):
        splits = list()
        last_value = group_by_list[0]
        for n in range(1, len(group_by_list)):
            if group_by_list[n] != last_value:
                splits.append(n)
                last_value = group_by_list[n]
        splits.append(len(group_by_list))
        return splits

    # read the file
    with open(path) as f:
        file_lines = [line for line in f.readlines()]

    # read the aero options
    n_aero_start, n_aero_end, len_label = find_aero_options(file_lines)
    aero_options = read_aero_options(
            file_lines[n_aero_start:n_aero_end], len_label
            )

    # find the polar data and read it
    n_results_header, n_results_start = find_results(file_lines)
    polars_raw = read_results(file_lines[n_results_start:],
            file_lines[n_results_header])

    # find the split positions
    # if the data should not be split, the split position is at the end of the
    # polar
    group_by = properties.get('group_by')
    if group_by is None:
        group_by = list(polars_raw.keys())[0]
    if group_by not in polars_raw:
        raise(LoadPolarError(f'Group "{group_by:s}" could not be found' \
                f' in "{path:s}"'))
    splits = find_group_by_splits(polars_raw[group_by])

    # create the polar-objects based on the splits
    polars = dict()
    last_split = 0
    for new_split in splits:
        polar = {key: polars_raw[key][last_split:new_split] for key in
                polars_raw.keys()}
        last_split = new_split

        unique_name = f'{properties["name"]}_{group_by}_{polar[group_by][0]}'
        unique_name_clean = re.sub("[^0-9a-zA-Z]+", "", unique_name)
        polars[unique_name_clean] =  AerodynamicPolar(polar, name=unique_name,
                solver="ADflow", solver_options=aero_options)

    return polars


load_switcher = {
        "adflow_utils": load_adflow_utils,
        }
lsk = list(load_switcher.keys())

class PolarList(ObjectList):
    list_type = Polar
    init_json_scheme = {
                "type": "array",
                "uniqueItems": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "file_type": {"anyOf":
                            [{'const': lsk[i]} for i in range(len(lsk))]
                            },
                        "file_name": {"type": "string"},
                        "file_properties": {"type": "object"},
                        },
                    "required": ["file_type"]
                    }
            }

    def load(self, path):
        for file in self.init_json:
            file_type = file["file_type"]
            file_name = file["file_name"]
            file_properties = file.get("file_properties", dict())
            file_path = os.path.join(path, file_name)

            func = load_switcher.get(file_type, load_file)
            polars = func(file_path, file_properties)
            self.container.update(polars)
