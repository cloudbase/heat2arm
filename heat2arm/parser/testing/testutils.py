# Copyright 2015 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
    This module contains functions generally useful throughout numerous
    testing scenarios.
"""


def recursive_dict_search(obj, key):
    """ recursive_dict_search returns a bool signaling whether or not a key is
    present in a dictionary. It traverses both nested dictionaries and lists
    which might be present among dictionary values recursively.
    """
    is_dict = type(obj) == dict
    is_list = type(obj) == list

    if not (is_dict or is_list):
        return False

    if is_list:
        return any([recursive_dict_search(item, key) for item in obj])

    if is_dict:
        if key in obj:
            return True
        else:
            return any(
                [recursive_dict_search(item, key) for item in obj.values()]
            )
