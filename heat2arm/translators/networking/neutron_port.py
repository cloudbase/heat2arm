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

from heat2arm.constants import ARM_API_2015_05_01_PREVIEW
from heat2arm.translators import base


class NeutronPortARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronPortARMTranslator is the translator associated to Neutron port.
    """
    heat_resource_type = "OS::Neutron::Port"
    # NOTE: will not be mapped into an ARM resource.
    arm_resource_type = None

    def get_variables(self):
        """ get_variables returns a dict of ARM template variables associated
        to this port.
        """
        return {
            "nicName_%s" % self._name: self._name,
        }

    def _get_floating_ip_resource_name(self):
        """ _get_floating_ip_resource_name is a helper method which returns the
        name of the Neutron Floating IP pool associated to the port resource.
        """
        for heat_resource in self._heat_resource.stack.iter_resources():
            if heat_resource.type() == "OS::Neutron::FloatingIP":
                port_resource = base.get_ref_heat_resource(
                    heat_resource, 'port_id')
                if port_resource is self._heat_resource:
                    return heat_resource.name

    def get_dependencies(self):
        """ get_dependencies returns a list of all the dependencies
        of the Neutron port.
        """
        floating_ip_resource_name = self._get_floating_ip_resource_name()

        heat_net_resource = base.get_ref_heat_resource(
            self._heat_resource, "network_id")
        net_name = heat_net_resource.name

        dependencies = [
            "[concat('Microsoft.Network/virtualNetworks/', "
            "variables('virtualNetworkName_%s'))]" % net_name
        ]

        if floating_ip_resource_name:
            dependencies.append(
                "[concat('Microsoft.Network/publicIPAddresses/', "
                "variables('publicIPAddressName_%s'))]" %
                floating_ip_resource_name
            )

        return dependencies

    def get_resource_data(self):
        """ get_resource_data returns the list of data associated to the port
        which is directly serializable into ARM template format.
        """
        heat_net_resource = base.get_ref_heat_resource(
            self._heat_resource, "network_id")
        net_name = heat_net_resource.name

        nic_properties_data = {
            # TODO: check the Heat net dhcp property
            "privateIPAllocationMethod": "Dynamic",
            "subnet": {
                "id":
                "[variables('virtualNetworkSubnetName_ref_%s')]" % net_name
            }
        }

        floating_ip_resource_name = self._get_floating_ip_resource_name()
        if floating_ip_resource_name:
            nic_properties_data["publicIPAddress"] = {
                "id": "[resourceId('Microsoft.Network/publicIPAddresses', "
                      "variables('publicIPAddressName_%s'))]" %
                      floating_ip_resource_name
            }

        return [{
            "apiVersion": ARM_API_2015_05_01_PREVIEW,
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[variables('nicName_%s')]" % self._name,
            "location": "[variables('location')]",
            "dependsOn": self.get_dependencies(),
            "properties": {
                "ipConfigurations": [{
                    "name": "ipconfig%s" % self._name,
                    "properties": nic_properties_data,
                }]
            }
        }]
