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
    Defines the base class of all template Resources.
"""

import json
import logging

LOG = logging.getLogger("__heat2arm__")


class Resource(object):
    """ Resource defines the basic properties of any resource.
    """

    # _type_field_name contains the string constant representing the name
    # of the type field of a resource.
    _type_field_name = ""

    # _properties_field_name contains the string constant representing
    # the name of the properties field of a resource.
    _properties_field_name = ""

    def __init__(self, name, data):
        """ A Resource is created provided the name of the resource and all the
        containing data.
        """
        self.name = name

        # check for the type field, which is mandatory:
        if self._type_field_name not in data:
            raise Exception("Provided resource has no '%s' field: '%s'" %
                            (self._type_field_name, self))
        self._type = data[self._type_field_name]

        # next, check for a properties field:
        if self._properties_field_name in data:
            self.properties = data[self._properties_field_name]
        else:
            self.properties = {}
            LOG.warn("Resource '%s' has no '%s' field.",
                     self.name, self._properties_field_name)

    def type(self):
        """ type returns this Resource's type name. """
        return self._type

    def __str__(self):
        """ __str__ simply returns the properties dict of the resource. """
        data = self.properties.copy()
        data.update({self._type_field_name: self._type})
        return json.dumps(data, indent=4)

    def __repr__(self):
        """ __repr__ simply returns a dict with the resource's name and
        properties.
        """
        return json.dumps({self.name: self.properties}, indent=4)
