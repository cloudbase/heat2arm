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
    This module contains general utility functions.
"""

import collections


def is_homogeneous(seq, types):
    """ is_homogeneous checks whether the provided list's elements are
    all an instance of one of the required types.
    """
    if (not isinstance(seq, collections.Sequence)) or (isinstance(seq, str)):
        return False

    for elem in seq:
        if type(elem) not in types:
            return False

    return True
