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
    Defines the base class for all the heat to ARM translators.
"""


def get_ref_heat_resource(heat_resource, property_name):
    """ get_ref_heat_resource is a helper function which returns the property
    with the given name from the given Heat resource object.
    """
    resource_name = heat_resource.properties.data[property_name].args
    return heat_resource.stack[resource_name]


class BaseHeatARMTranslator(object):
    """ BaseHeatARMTranslator is the base class for all heat to ARM translators

    It defines stubs for common functions required of a translator.
    """
    # fields for keeping the corresponding heat and ARM resource types
    # the this translator maps to/from:
    heat_resource_type = None
    arm_resource_type = None

    def __init__(self, heat_resource):
        self._heat_resource = heat_resource
        self._name = self._heat_resource.name

    def _make_var_name(self, var):
        """ _get_var_name is a helper method which constructs the
        name to be used as an ARM template variable.
        The result is of the form <parameter_name>_<self._name>.
        """
        return "%s_%s" % (var, self._name)

    def get_parameters(self):
        """ get_parameters returns the dict of ARM template parameters
        associated with the Heat template's resource translation.
        """
        return {}

    def get_variables(self):
        """ get_variables returns the dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        return {}

    def get_dependencies(self):
        """ get_dependencies returns the list of resources which are
        required by this resource.
        """
        return []

    def get_resource_data(self):
        """ get_resource_data returns a list of all the characteristics
        representing the resource which can be directly serialized
        into the resulting ARM template format.
        """
        return []
