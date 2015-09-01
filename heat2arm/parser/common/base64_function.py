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
    Contains the definition for the base class of base64 encoding functions.
"""

from heat2arm.parser.function import Function


class Base64Function(Function):
    """ Base64Function is the base class for all base64-encoding functions.

    It takes the form:

        " 'Base64Function': 'string' "
    """

    def _check_args(self, args):
        """ _check_args checks the validity of the provided arguments. """
        if not isinstance(args, str):
            raise Exception("Base64 function expected string parameter, "
                            "got: '%s'" % args)

    def apply(self, args):
        """ apply applies the function to the given arguments and returns
        the result.

        NOTE: because we don't actually want the base64 conversion to occur
        here, we simply return the string as-is:
        """
        self ._check_args(args)
        return args
