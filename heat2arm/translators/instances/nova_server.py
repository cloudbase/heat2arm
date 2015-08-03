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
    Defines the translator and utilities for mapping
    a Nova server to an Azure VM.
"""

import logging

from heat2arm.translators.instances.base_instance import (
    BaseInstanceARMTranslator
)
from heat2arm.translators.instances import nova_utils as utils

LOG = logging.getLogger(__name__)


class NovaServerARMTranslator(BaseInstanceARMTranslator):
    """ NovaServerARMTranslator is the translator associated to a Nova server.

    It processes the fields and parameters of a Nova server defined in Heat.
    """
    heat_resource_type = "OS::Nova::Server"

    def get_variables(self):
        """ get_variables returns the dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        base_vars = self._get_base_variables()

        (publisher, offer, sku) = utils.get_azure_image_info(
            self._heat_resource.properties['image'])

        base_vars.update({
            "vmSize_%s" % self._name: utils.get_azure_flavor(
                self._heat_resource.properties['flavor']),
            "imgPublisher_%s" % self._name: publisher,
            "imgOffer_%s" % self._name: offer,
            "imgSku_%s" % self._name: sku,
        })

        return base_vars

    # NOTE:the following methods are inherited from BaseInstanceARMTranslator:
    #   - get_parameters.
    #   - get_dependencies.
    #   - get_resource_data.
    #   - update_context.

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_names is a helper method which returns a
        list containing the names of all port resources which are referenced
        by this Nova server.
        """
        port_resource_names = []

        if 'networks' in self._heat_resource.properties.data:
            for port_data in self._heat_resource.properties.data["networks"]:
                if 'port' in port_data:
                    port_resource_names.append(port_data['port'].args)

        return port_resource_names

    def _get_userdata(self):
        """ _get_userdata is a helper method which returns the userdata
        from the instance's definition, if any.
        """
        if 'user_data' in self._heat_resource.properties:
            return self._heat_resource.properties['user_data']

        return ""
