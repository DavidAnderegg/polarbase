import re
from operator import  or_
from functools import reduce



def str2number(s):
    """converts a string to int or float if possible
    if it is neither, it returns the string itself"""

    # check fo int
    is_int = False
    if s[0] in ('-', '+'):
        is_int = s[1:].isdigit()
    else:
        is_int = s.isdigit()

    if is_int:
        return int(s)

    # check for float
    try:
        return float(s)
    except ValueError:
        return s

def str2value(string):
    """ This function takes any string and coverts it a python datatype. If
    possible it converts it to a list"""

    # clean string
    string = ' '.join(string.split())

    # check if it could be a list
    list_chars = '[], ' # if any of those characters is found, it is assumed to
                        # be a list
    if reduce(or_, map(string.__contains__, list_chars)):
        #remove unneeded brackets
        remove_chars = '[]'
        for c in remove_chars:
            string = string.replace(c, '')

        # split it
        string = ' '.join(string.split())
        list_string = re.split(' |, |,|\n', string)

        # convert all strings to numbers if possible
        result = list()
        for item in list_string:
            result.append(str2number(item))

        return result

    # if it is no list, try to convert it to a number
    result = str2number(string)

    return result
