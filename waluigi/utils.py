#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    
"""

import pickle
from collections import Iterable

import six


def no_op(*a, **kw):
    return


def save_object(any_object, filename):
    """Saves any python obect to pickle(INSECURE)"""
    import pickle
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(any_object, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    """Loads any python obect to pickle(INSECURE)"""
    import pickle
    with open(filename, 'rb') as pickled:
        variable = pickle.load(pickled)
    return variable


def ensure_iterable(iter_or_str):
    if isinstance(iter_or_str, Iterable) and not isinstance(iter_or_str, six.string_types):
        return iter_or_str
    else:
        return {iter_or_str, }
