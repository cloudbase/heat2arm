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
    Defines the translator for a Neutron port resource.
"""

from heat2arm.translators.base import get_ref_heat_resource
from heat2arm.translators.networking.nics.base_nic import BaseNICARMTranslator


class NeutronPortARMTranslator(BaseNICARMTranslator):
    """ NeutronPortARMTranslator is the translator associated to Neutron port.

    The closest resource to it on Azure would be a virtual network interface,
    which is what a translation of this resource results in.
    """
    heat_resource_type = "OS::Neutron::Port"
    arm_resource_type = "Microsoft.Network/networkInterfaces"

    # NOTE: the following are inherited from BaseNICARMTranslator:
    #   - get_variables
    #   - get_dependencies
    #   - get_resource_data

    def _get_floating_ip_resource_name(self):
        """ _get_floating_ip_resource_name is a helper function which
        returns the name of the floating IP resource associated to
        this NIC-like resource.
        """
        for heat_resource in self._heat_resource.stack.iter_resources():
            if heat_resource.type() == "OS::Neutron::FloatingIP":
                port_resource = get_ref_heat_resource(
                    heat_resource, 'port_id')
                if port_resource is self._heat_resource:
                    return heat_resource.name

    def _get_ref_network(self):
        """ _get_ref_network is a helper function which returns the name
        of the network which references this NIC-like resource.
        """
        if "network_id" in self._heat_resource.properties.data:
            return get_ref_heat_resource(self._heat_resource, "network_id")
