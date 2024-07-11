# Simple tools for working with python lists

def _grep(_list, needle):
    """returns a generator that can iterate over list items that contain 'needle'"""
    if type(needle) is not list:
        needle = [ needle ]
    for l in _list:
        for n in needle:
            if n in str(l):
                yield l
                break

def grep(_list, needle):
    """returns a list of items from _list that contain 'needle'
    
    _list - the iterable to search
    needle - a string or list of strings to search for """
    return list(_grep(_list, needle))
