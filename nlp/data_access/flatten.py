#!/usr/bin/env python


# The code below has been extracted with modifications from
# https://github.com/amirziai/flatten.git, which is distributed with the
# following license:

# MIT License

# Copyright (c) 2016 Amir Ziai

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def _construct_key(previous_key, separator, new_key):
    """
    Returns the new_key if no previous key exists, otherwise concatenates
    previous key, separator, and new_key
    :param previous_key:
    :param separator:
    :param new_key:
    :return: a string if previous_key exists and simply passes through the
    new_key otherwise
    """
    if previous_key:
        return u"{}{}{}".format(previous_key, separator, new_key)
    else:
        return new_key


def flatten(nested_dict, separator="_", root_keys_to_ignore=set()):
    """
    Flattens a dictionary with nested structure to a dictionary with no
    hierarchy
    Consider ignoring keys that you are not interested in to prevent
    unnecessary processing
    This is specially true for very deep objects

    :param nested_dict: dictionary we want to flatten
    :param separator: string to separate dictionary keys by
    :param root_keys_to_ignore: set of root keys to ignore from flattening
    :return: flattened dictionary
    """
    assert isinstance(nested_dict, dict), "flatten requires a dictionary input"
    assert isinstance(separator, str), "separator must be string"

    # This global dictionary stores the flattened keys and values and is
    # ultimately returned
    flattened_dict = dict()

    def _flatten(object_, key):
        """
        For dict, list and set objects_ calls itself on the elements and for
        other types assigns the object_ to
        the corresponding key in the global flattened_dict
        :param object_: object to flatten
        :param key: carries the concatenated key for the object_
        :return: None
        """
        # Empty object can't be iterated, take as is
        if not object_:
            flattened_dict[key] = object_
        # These object types support iteration
        elif isinstance(object_, dict):
            for object_key in object_:
                if not (not key and object_key in root_keys_to_ignore):
                    _flatten(object_[object_key], _construct_key(key,
                                                                 separator,
                                                                 object_key))
        elif isinstance(object_, (list, set, tuple)):
            for index, item in enumerate(object_):
                _flatten(item, _construct_key(key, separator, index))
        # Anything left take as is
        else:
            flattened_dict[key] = object_

    _flatten(nested_dict, None)
    return flattened_dict
