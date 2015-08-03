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
    Defines the base implementation for ARM NIC resource translators.
"""

from heat2arm import constants
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseNICARMTranslator(BaseHeatARMTranslator):
    """ BaseARMNICTranslator contains the base implementation for all
    translators which map resources to Azure NICs.
    """
    heat_resource_type = None
    arm_resource_type = "Microsoft.Network/networkInterfaces"

    def get_variables(self):
        """ get_variables returns a dict of ARM template variables associated
        to the translation.
        """
        return {
            "nicName_%s" % self._name: self._name,
        }

    def _get_floating_ip_resource_name(self):
        """ _get_floating_ip_resource_name is a helper function which
        returns the name of the floating IP resource associated to
        this NIC-like resource.

        It must be implemented by all inheriting classes.
        """
        pass

    def _get_ref_network(self):
        """ _get_ref_network is a helper function which returns the name
        of the network which references this NIC-like resource.

        NOTE: It is stubbed and must be implemented by all inheriting classes.
        """
        pass

    def get_dependencies(self):
        """ get_dependencies returns a list of all the dependencies
        of the NIC-like resource.
        """
        floating_ip_resource_name = self._get_floating_ip_resource_name()

        heat_net_resource = self._get_ref_network()
        if heat_net_resource:
            net_name = heat_net_resource.name
            dependencies = [
                "[concat('Microsoft.Network/virtualNetworks/', "
                "variables('virtualNetworkName_%s'))]" % net_name
            ]
        else:
            dependencies = [
                "[concat('Microsoft.Network/virtualNetworks/', "
                "parameters('newVirtualNetworkName'))]"
            ]

        if floating_ip_resource_name:
            dependencies.append(
                "[concat('Microsoft.Network/publicIPAddresses/', "
                "variables('publicIPAddressName_%s'))]" %
                floating_ip_resource_name
            )

        return dependencies

    def get_resource_data(self):
        """ get_resource_data returns the list of data associated to resource
        which is directly serializable into ARM template format.
        """
        heat_net_resource = self._get_ref_network()
        if heat_net_resource:
            net_name = heat_net_resource.name
            subnet_id = ("[variables('virtualNetworkSubnetName_ref_%s')]" %
                         net_name)
        else:
            subnet_id = "[variables('defaultSubnetRef')]"

        nic_properties_data = {
            "privateIPAllocationMethod": "Dynamic",
            "subnet": {
                "id": subnet_id
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
            "apiVersion": constants.ARM_API_VERSION,
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
