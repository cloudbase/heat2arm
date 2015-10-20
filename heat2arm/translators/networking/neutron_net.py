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
    Defines translators for mapping Neutron networking resources
    to an Azure Virtual Network resource.

    ARM Network Resource Provider:
https://azure.microsoft.com/en-gb/documentation/articles/resource-groups-networking/
"""

from heat2arm.config import CONF
from heat2arm.translators.base import BaseHeatARMTranslator


class NeutronNetARMTranslator(BaseHeatARMTranslator):
    """ NeutronNetARMTranslator is the translator for Neutron networks.

    Despite not having a direct stand-alone equivalent;
    Neutron networks can be modeled as Azure Virtual
    Networks together with some additional sub-components.

    This translator's only purpose is setting up all the variables
    required for the later definition of the equivalent Virtual Network
    by the NeutronSubnetARMTranslator translator.
    """
    heat_resource_type = "OS::Neutron::Net"
    # NOTE: will not be mapped into an ARM resource.
    arm_resource_type = None

    def get_variables(self):
        super(NeutronNetARMTranslator, self).get_variables()

        return {
            "virtualNetworkName_%s" % self._heat_resource_name:
                self._heat_resource_name,
            "virtualNetworkSubnetName_%s" % self._heat_resource_name:
            "%s_subnet1" % self._heat_resource_name,
            "virtualNetworkName_ref_%s" % self._heat_resource_name:
            "[resourceId('Microsoft.Network/virtualNetworks', "
            "variables('virtualNetworkName_%s'))]" % self._heat_resource_name,
            "virtualNetworkSubnetName_ref_%s" % self._heat_resource_name:
            "[concat(variables('virtualNetworkName_ref_%(net_name)s'),"
            "'/subnets/',variables('virtualNetworkSubnetName_%(net_name)s'))]"
            % {"net_name": self._heat_resource_name}
        }


class NeutronSubnetARMTranslator(BaseHeatARMTranslator):
    """ NeutronSubnetARMTranslator is the translator associated
    to a Neutron subnet.

    This translator leads to the defining of a new virtual network; as
    Neutron nets themselves have no real resulting translation without them.
    """
    heat_resource_type = "OS::Neutron::Subnet"
    arm_resource_type = "Microsoft.Network/virtualNetworks"

    def get_variables(self):
        """ get_variables resurns the dict of ARM template
        variables associated with the Neutron subnet.

        """
        super(NeutronSubnetARMTranslator, self).get_variables()

        cidr = self._heat_resource.properties['cidr']
        return {
            "subNetAddressPrefix_%s" % self._heat_resource_name: cidr
        }

    def get_resource_data(self):
        """ get_resource_data retuns the list of all characteristics
        representing the subnet which can be directly serialized into
        the ARM template format.
        """
        super(NeutronSubnetARMTranslator, self).get_resource_data()

        net_name = self._context.heat_resource_stack[
            self._heat_resource.properties["network"]
        ].name

        return [{
            "apiVersion": CONF.arm_api_version,
            "type": "Microsoft.Network/virtualNetworks",
            "name":
            "[variables('virtualNetworkName_%s')]" % net_name,
            "location": "[variables('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        # TODO: support multiple subnets
                        "[variables('subNetAddressPrefix_%s')]" % (
                            self._heat_resource_name
                        )
                    ]
                },
                "subnets": [{
                    # TODO: support multiple subnets
                    # Main issue here is that ARM networkInterfaces contain a
                    # reference to a subnet, while a Neutron port contains a
                    # reference to a network
                    "name":
                    "[variables('virtualNetworkSubnetName_%s')]" % net_name,
                    "properties": {
                        "addressPrefix":
                        "[variables('subNetAddressPrefix_%s')]" % (
                            self._heat_resource_name
                        )
                    }
                }]
            }
        }]
