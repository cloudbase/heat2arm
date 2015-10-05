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
    Contains the definition for the base class of all resource attribute
    getting options.
"""

import collections
import logging

from heat2arm.parser.common.exceptions import (FunctionApplicationException,
                                               FunctionArgumentException)
from heat2arm.parser.common.function import Function
from heat2arm.parser.common.functions.utils import is_homogeneous


LOG = logging.getLogger("__heat2arm__")


class GetAttrFunction(Function):
    """ GetAttrFunction is the base class for resource attribute
    getter functions.

    It takes the form:

        " 'GetAttrFunction': [ 'ResourceName', 'AttributeName', ... ] "
    """

    # _properties_field_name stores the name for the properties field
    # of a resource:
    _properties_field_name = ""

    # _exceptions is a dict of attributes whose getting is not necessary and
    # the associated default value to be used.
    # ex: CFN's GetAtt for an AvailabilityZone.
    _exceptions = {}

    def _check_args(self, args):
        """ _check_args is a helper method for checking the validity
        of the arguments provided.
        """
        if not isinstance(args, list) or not len(args) >= 2:
            raise FunctionArgumentException("Argument of attribute getter "
                                            "function '%s' must be a list of "
                                            "indeces; got: '%s'" % (
                                                self.name,
                                                args
                                            ))

        if not is_homogeneous(args, (str, int)):
            raise FunctionArgumentException(
                "'%s': argument must be a list of strings; got: '%s'" %
                (self.name, args)
            )

    def _get_item(self, cont, index):
        """ _get_item is a helper method which returns field with the given
        name/index from the given container object:
        """
        # make sure the given object is a container:
        if not isinstance(cont, collections.Container):
            raise Exception("'%s': not a container: cannot index '%s' in '%s'"
                            % (self.name, index, cont))

        # try and return the element. Even an exception may or may
        # not be specified (ex: CFN's GetAtt: AvailabilityZone):
        try:
            # NOTE: we can't just test with 'in' here as we may
            # be trying to index a list:
            return cont[index]
        except (IndexError, KeyError):
            # if not found; make sure it's not an exception:
            if index in self._exceptions:
                # just log the event and return the arg directly:
                LOG.warn("'%s': get exception applied for '%s'. Defaulting to"
                         " '%s'.", self.name, index, self._exceptions[index])
                return self._exceptions[index]
            else:
                # rock bottom:
                raise FunctionApplicationException(
                    "'%s': index '%s' missing from :'%s'" % (
                        self.name, index, cont
                    )
                )

    def apply(self, args):
        """ apply applies the function to the given set of arguments and
        returns the result:
        """
        self._check_args(args)

        # check if the resource exists:
        if args[0] in self._template.resources:
            # if so, procedurally index the resource for the desired info:
            res = self._template.resources[args[0]]

            if self._properties_field_name not in res:
                raise FunctionApplicationException(
                    "'%s': resource has no '%s' field: '%s'." %
                    (self.name, self._properties_field_name, res)
                )

            indexes = [self._properties_field_name] + args[1:]

            for i in indexes:
                res = self._get_item(res, i)
            return res
        else:
            raise FunctionApplicationException(
                "%s: resource '%s' does not exist." % (
                    self.name, args[0]
                )
            )
