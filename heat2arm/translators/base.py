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

import logging


class BaseHeatARMTranslator(object):
    """ BaseHeatARMTranslator is the base class for all heat to ARM translators

    It defines stubs for common functions required of a translator.
    """
    # fields for keeping the corresponding heat and ARM resource types
    # the this translator maps to/from:
    heat_resource_type = None
    arm_resource_type = None

    def __init__(self, heat_resource, context):
        self._heat_resource = heat_resource
        self._heat_resource_name = self._heat_resource.name
        self._context = context
        self._logger = logging.getLogger("__heat2arm__.%s" % (self,))

    def __str__(self):
        """ __str__ returns a formatted string containing the translator's
        name and the resource assigned to the translator.
        """
        return "%s(%s)" % (self.__class__.__name__, self._heat_resource.name)

    def get_parameters(self):
        """ get_parameters returns the dict of ARM template parameters
        associated with the Heat template's resource translation.
        """
        self._logger.debug("get_parameters was called.")
        return {}

    def get_variables(self):
        """ get_variables returns the dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        self._logger.debug("get_variables was called.")
        return {}

    def get_dependencies(self):
        """ get_dependencies returns the list of resources which are
        required by this resource.
        """
        self._logger.debug("get_dependencies was called.")
        return []

    def get_resource_data(self):
        """ get_resource_data returns a list of all the characteristics
        representing the resource which can be directly serialized
        into the resulting ARM template format.
        """
        self._logger.debug("get_resource_data was called.")
        return {}

    def update_context(self):
        """ update_context applies any changes necessary for the completeness
        of the resource's translation over the parameters, variables and
        resources stored within the context.

        NOTE: it should be called after translate to ensure the resources which
        must be updated from the context have already been translated.
        """
        self._logger.debug("update_context was called.")
        return

    def translate(self):
        """ translate is the main method of a translator; it adds all the
        required parameters, variables and resource data to the context.
        """
        self._logger.debug("first translation pass initiated.")

        self._context.add_parameters(self.get_parameters())
        self._context.add_variables(self.get_variables())
        for resource in self.get_resource_data():
            # NOTE: adding check here in the case of resources which are indeed
            # translated under different resource translator's functions but
            # do not result in any resource data themselves.
            if resource:
                self._context.add_resource(resource)

    def _make_var_name(self, var):
        """ _get_var_name is a helper method which constructs the
        name to be used as an ARM template variable.
        The result is of the form <parameter_name>_<self._heat_resource_name>.
        """
        return "%s_%s" % (var, self._heat_resource_name)
