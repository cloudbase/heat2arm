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
    Defines the base class for all map-referencing functions.
"""

from heat2arm.parser.common.exceptions import (FunctionApplicationException,
                                               FunctionArgumentException)
from heat2arm.parser.common.function import Function
from heat2arm.parser.common.functions.utils import is_homogeneous


class MapFindFunction(Function):
    """ MapFindFunction is the base class for all map-referencing functions,

    It takes the form:

        " 'MapFindFunction': [ 'MapName', 'KeyName', 'ValueName'] "
    """

    def _check_args(self, args):
        """ _check_args validates the provided set of arguments. """
        # check if list:
        if not is_homogeneous(args, (str,)):
            raise FunctionArgumentException(
                "Argument of mapping function '%s' must be a list;"
                "of strings; got: '%s'" % (self.name, args)
            )

        # check if list of proper length:
        if not len(args) == 3:
            raise FunctionArgumentException(
                "%s: argument list must have the three elements;"
                " got: '%s'" % (self.name, args)
            )

    def apply(self, args):
        """ apply applies the function on the given set of arguments and
        returns the result.
        """
        self._check_args(args)

        # first, check for the name of the mapping:
        map_name = args[0]
        if map_name not in self._template.variables:
            raise FunctionApplicationException(
                "%s: could not find defined mapping '%s'" % (
                    self.name,
                    map_name
                )
            )
        mapping = self._template.variables[map_name]

        # then, check for the key:
        key = args[1]
        if key not in mapping:
            raise FunctionApplicationException(
                "%s: could not find key '%s' in mapping '%s'" %
                (self.name, key, map_name)
            )
        mapping = mapping[key]

        # and last, check for the value:
        value = args[2]
        if value not in mapping:
            raise FunctionApplicationException(
                "%s: could not find value '%s' in mapping '%s'" % (
                    self.name,
                    value,
                    mapping
                )
            )

        # if here; can return the value directly:
        return mapping[value]
