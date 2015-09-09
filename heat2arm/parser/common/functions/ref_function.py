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
    Contains the definition of the base class for referencing functions.
"""

import logging

from heat2arm.parser.common.exceptions import (FunctionApplicationException,
                                               FunctionArgumentException)
from heat2arm.parser.common.function import Function


LOG = logging.getLogger("__heat2arm__")


class RefFunction(Function):
    """ RefFunction is the base class for all functions which implement the
    simple referencing mechanic.

    It takes the form:

        " 'RefFunction': 'RefName' "

    It simply returns the default value of the specified parameter or the
    referenced resource.
    """

    # for the parameter accessing functions, define the default
    # field's name of the parameter's definition.
    _param_default_field_name = ""

    def _check_args(self, args):
        """ _check_args validates the provided set of arguments. """
        if not isinstance(args, str):
            raise FunctionArgumentException(
                "Referencing function '%s' expects a "
                "single string parameter, but got: '%s'" % (
                    self.name,
                    args
                )
            )

    def apply(self, args):
        """ apply applies the function to the given set of data and returns
        the result.
        """
        self._check_args(args)

        # check if reference is for a parameter:
        if args in self._template.parameters:
            # if so, check if it has a default field:
            if (self._param_default_field_name in
                    self._template.parameters[args]):
                # return the default value.
                return self._template.parameters[args][
                    self._param_default_field_name
                ]
            else:
                # the value might not be necessary, so we just log a warning
                # and return the provided args:
                LOG.warning("Default field for parameter '%s' was not provided;"
                            " ignoring in case it wasn't really needed.", args)
                return args

        # else, it must be a reference to another resource, in which case
        # we trivially return the resource's name if present:
        if args in self._template.resources:
            return args

        # else, rock bottom:
        raise FunctionApplicationException(
            "Invalid referencing with '%s'. Reference to '%s' "
            "could not be resolved." % (
                self.name,
                args
            )
        )
