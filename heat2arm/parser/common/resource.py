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

from heat2arm.parser.common import exceptions

LOG = logging.getLogger("__heat2arm__.Resource")


class Resource(object):
    """ Resource defines the basic properties of any resource.

    It makes available the data organised through the following fields:
        - name - the name of the resource
        - properties - the dict of properties for the Resource
        - meta - the dict of metadata for the resource (if applicable)
        - type - the type of the resource
    """

    # _type_field_name contains the string constant representing the name
    # of the type field of a resource.
    _type_field_name = ""

    # _meta_field_name contains the string constant representing the the
    # name of the meta field of a resource (if applicable).
    _meta_field_name = ""

    # _properties_field_name contains the string constant representing
    # the name of the properties field of a resource.
    _properties_field_name = ""

    def __init__(self, name, data):
        """ A Resource is created provided the name of the resource and all the
        containing data.
        """
        if not name:
            raise exceptions.ResourceNameMissingException(
                "No name given to resource."
            )
        self.name = name

        # check for the type field, which is mandatory:
        if self._type_field_name not in data:
            raise exceptions.ResourceTypeMissingException(
                "Resource '%s' has no '%s' field." % (
                    self.name,
                    self._type_field_name
                )
            )
        self.type = data[self._type_field_name]

        # check for the meta field (if one is even available):
        if self._meta_field_name and self._meta_field_name in data:
            self.meta = data[self._meta_field_name]
        else:
            self.meta = {}

        # next, check for a properties field:
        if self._properties_field_name in data:
            self.properties = data[self._properties_field_name]
        else:
            self.properties = {}
            LOG.warn("Resource '%s' has no '%s' field.",
                     self.name, self._properties_field_name)

    def __str__(self):
        """ __str__ simply returns a pretty JSON interpretation
        of the data which characterises the resource.
        """
        return json.dumps(self.properties, indent=4)

    def __repr__(self):
        """ __repr__ simply returns a JSON interpretation of the data
        which characterises the resource in a dict under the
        resource's name.
        """
        return json.dumps({self.name: self.properties})
