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
    Defines the base class for all the argument joining functions.
"""

from functools import reduce

from heat2arm.parser.function import Function
from heat2arm.parser.common.utils import is_homogeneous


class JoinFunction(Function):
    """ JoinFunction is the base class for all function which
    join their provided arguments.

    It takes the form:

        " 'JoinFunction': [ "delimiter", ['elem1', 'elem2', ...] ] "

    It simply joins all of the elements it is provided with the
    given delimiter.
    """

    def _check_args(self, args):
        """ _check_args validates the provided set of arguments. """
        if not isinstance(args[0], str):
            raise Exception(
                "First argument of joining function  '%s' must be a string"
                ", got: '%s'" % (self.name, type(args))
            )

        if not is_homogeneous(args[1], str):
            raise Exception("Second argument of joining function  '%s' must "
                            "be a list of strings, got: '%s'" % (self.name,
                                                                 args))

    def apply(self, args):
        """ apply applies the function to the given set of arguments
        and returns the result.
        """
        self._check_args(args)

        sep = args[0]
        return reduce(lambda x, y: sep.join([x, y]), args[1])
