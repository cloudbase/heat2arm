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
    Defines the base translator for floating IP resource types.
"""

from heat2arm import constants
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseFloatingIPARMTranslator(BaseHeatARMTranslator):
    """ BaseFloatingIPARMTranslator provides the base implementation for
    all inheriting floating IP resource type translators.
    """
    heat_resource_type = None
    arm_resource_type = "Microsoft.Network/publicIPAddresses"

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
            "apiVersion": constants.ARM_API_VERSION,
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
