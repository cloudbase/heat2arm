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
    Defines translators for mapping Neutron
    networking resources to Azure ones.
"""

from heat2arm import constants
from heat2arm.translators import base

'''
ARM Network Resource Provider:
https://azure.microsoft.com/en-gb/documentation/articles/resource-groups-networking/
'''


class NeutronNetARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronNetARMTranslator is the translator for Neutron networks.

    Despite not having a direct stand-alone equivalent;
    Neutron networks can be modeled as Azure virtual
    networks together with some additional sub-components.
    """
    # No direct ARM resource translation
    # Azure virtual networks encompass both Neutron networks and subnets
    heat_resource_type = "OS::Neutron::Net"

    def get_variables(self):
        return {
            "virtualNetworkName_%s" % self._name: self._name,
            "virtualNetworkSubnetName_%s" % self._name:
            "%s_subnet1" % self._name,
            "virtualNetworkName_ref_%s" % self._name:
            "[resourceId('Microsoft.Network/virtualNetworks', "
            "variables('virtualNetworkName_%s'))]" % self._name,
            "virtualNetworkSubnetName_ref_%s" % self._name:
            "[concat(variables('virtualNetworkName_ref_%(net_name)s'),"
            "'/subnets/',variables('virtualNetworkSubnetName_%(net_name)s'))]"
            % {"net_name": self._name}
        }


class NeutronSubnetARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronSubnetARMTranslator is the translator associated
    to a Neutron subnet.

    Because of the way Azure handles subnets (as being an integral part of a
    vitual network); this translator is used merely as a helper for the main
    NeutronNetARMTranslator.
    """
    heat_resource_type = "OS::Neutron::Subnet"
    # NOTE: will not be mapped into an ARM resource.
    arm_resource_type = None

    def get_variables(self):
        """ get_variables resurns the dict of ARM template
        variables associated with the Neutron subnet.

        """
        cidr = self._heat_resource.properties['cidr']
        return {
            "subNetAddressPrefix_%s" % self._name: cidr
        }

    def get_resource_data(self):
        """ get_resource_data retuns the list of all characteristics
        representing the subnet which can be directly serialized into
        the ARM template format.
        """
        heat_net_resource = base.get_ref_heat_resource(
            self._heat_resource, "network_id")
        net_name = heat_net_resource.name

        return [{
            "apiVersion": constants.ARM_API_2015_05_01_PREVIEW,
            "type": "Microsoft.Network/virtualNetworks",
            "name":
            "[variables('virtualNetworkName_%s')]" % net_name,
            "location": "[variables('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        # TODO: support multiple subnets
                        "[variables('subNetAddressPrefix_%s')]" % self._name
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
                        "[variables('subNetAddressPrefix_%s')]" % self._name
                    }
                }]
            }
        }]


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
            "apiVersion": constants.ARM_API_2015_05_01_PREVIEW,
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


class NeutronFloatingIPARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronFloatingIPARMTranslator is the translator associated to a
    Neutron floating IP range.
    """
    heat_resource_type = "OS::Neutron::FloatingIP"
    # NOTE: will not be mapped into an ARM resource.
    arm_resource_type = None

    def get_parameters(self):
        """ get_parameters returns a dict of all the parameters associated
        to the Neutron floating IP.
        """
        return {
            "dnsNameForPublicIP_%s" % self._name: {
                "type": "string",
                "metadata": {
                    "description": "Unique DNS name for public IP address."
                }
            },
        }

    def get_variables(self):
        """ get_variables returns a dict of ARM template variables associated
        with the Neutron Floating IP's translation.
        """
        return {
            "publicIPAddressName_%s" % self._name: self._name,
        }

    def get_resource_data(self):
        """ get_resource_data returns a list of all the characterisics
        respresenting the resource which can directly be serialized
        into the resulting ARM template format.
        """
        return [{
            "apiVersion": constants.ARM_API_2015_05_01_PREVIEW,
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[variables('publicIPAddressName_%s')]" % self._name,
            "location": "[variables('location')]",
            "properties": {
                # TODO: Add support for static IPs
                "publicIPAllocationMethod": "Dynamic",
                "dnsSettings": {
                    "domainNameLabel":
                    "[parameters('dnsNameForPublicIP_%s')]" % self._name
                    }
                }
            }]


class NeutronRouterARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronRouterARMTranslator is the translator for a Neutron router.

    It has no direct Azure equivalent; so its translation is thus empty.
    """
    # No direct ARM resource translation
    heat_resource_type = "OS::Neutron::Router"


class NeutronRouterInterfaceARMTranslator(base.BaseHeatARMTranslator):
    """ NeutronRouterInterfaceARMTranslator is the translator
    for a Neutron router resource.

    It has no direct Azure equivalent; so its translation is thus empty.
    """
    # No direct ARM resource translation
    heat_resource_type = "OS::Neutron::RouterInterface"
