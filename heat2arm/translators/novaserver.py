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

import json
from oslo_config import cfg

from heat2arm import constants
from heat2arm.translators import base

LOG = logging.getLogger(__name__)

# Get the config instance and add options:
CONF = cfg.CONF
CONF.register_opts([
    # Dict option for mapping Nova sizes to Azure sizes:
    cfg.DictOpt(
        'vm_flavor_size_map',
        default={
            'm1.tiny': "Basic_A0",
            'm1.small': "Basic_A1",
            'm1.medium': "Basic_A2",
            'm1.large': "Basic_A3",
            'm1.xlarge': "Basic_A4",
        },
        help='A map between OpenStack Nova flavors and Azure VM sizes'),
    # Default size:
    cfg.StrOpt(
        'vm_default_size',
        default="Basic_A1",
        help='Default Azure size in case an OpenStack Nova flavor '
             'could not be mapped'),
    # Mapping between Nova image names and Azure images:
    # TODO: ideally; find a way to auto-fetch these...
    cfg.DictOpt(
        'vm_image_map',
        default={
            'ubuntu.12.04.LTS.x86_64':
            "Canonical;UbuntuServer;12.04.5-LTS",
        },
        help='A map between OpenStack Nova and Azure VM images'),
])


def get_azure_flavor(nova_flavor):
    """ get_azure_flavor is a helper funcion which returns the appropriate
    Azure VM size corresponding to the given Nova flavor or a sensible default.
    """
    return CONF.vm_flavor_size_map.get(nova_flavor, CONF.vm_default_size)


def get_azure_image_info(nova_image):
    """ get_azure_image_info is a helper function which returns
    the info of the image. """
    azure_image_info_str = CONF.vm_image_map.get(nova_image)
    if not azure_image_info_str:
        raise Exception(
            'Nova image "%s" cannot be mapped to an Azure equivalent. Please '
            'update the "vm_image_map" configuration option' % nova_image)

    azure_image_info = tuple(azure_image_info_str.split(";"))
    if len(azure_image_info) != 3:
        raise Exception(
            '"%s" does not contain valid Azure image data. The required '
            'format is "publisher;offer;sku"')

    return azure_image_info


class NovaServerARMTranslator(base.BaseHeatARMTranslator):
    """ NovaServerARMTranslator is the translator associated to a Nova server.

    It processes the fields and parameters of a Nova server.
    """
    heat_resource_type = "OS::Nova::Server"
    arm_resource_type = "Microsoft.Compute/virtualMachines"

    def get_variables(self):
        """ get_variables returns the dict of ARM template variables
        associated with the Heat template's translation.
        """
        (publisher, offer, sku) = get_azure_image_info(
            self._heat_resource.properties['image'])

        return {
            "vmName_%s" % self._name: self._name,
            "vmSize_%s" % self._name: get_azure_flavor(
                self._heat_resource.properties['flavor']),
            "imgPublisher_%s" % self._name: publisher,
            "imgOffer_%s" % self._name: offer,
            "imgSku_%s" % self._name: sku,
        }

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_names is a helper method which returns a
        list containing the names of all the port resources.
        """
        port_resource_names = []

        if 'networks' in self._heat_resource.properties.data:
            for port_data in self._heat_resource.properties.data["networks"]:
                port_resource_names.append(port_data['port'].args)

        return port_resource_names

    def _get_network_interfaces(self):
        """ _get_network_interfaces is a helper method which returns a list of
        all the network interfaces associated to the machine.
        """
        network_interfaces_data = []

        for port_resource_name in self._get_ref_port_resource_names():
            network_interfaces_data.append({
                "id": "[resourceId('Microsoft.Network/networkInterfaces', "
                      "variables('nicName_%s'))]" % port_resource_name
            })

        return network_interfaces_data

    def _get_vm_properties(self):
        """ _get_vm_properties is a helper method which returns the dict with
        all the auxiliary properties associated to the machine:
        """
        os_profile_data = {
            "computername": "[variables('vmName_%s')]" % self._name,
            "adminUsername": "[parameters('adminUsername')]",
            "adminPassword": "[parameters('adminPassword')]"
        }

        user_data = self._heat_resource.properties['user_data']
        if user_data:
            os_profile_data["customData"] = (
                "[base64('%s')]" % json.dumps(user_data))

        return {
            "hardwareProfile": {
                "vmSize": "[variables('vmSize_%s')]" % self._name
            },
            "osProfile": os_profile_data,
            "storageProfile": {
                "imageReference": {
                    "publisher": "[variables('imgPublisher_%s')]" % self._name,
                    "offer": "[variables('imgOffer_%s')]" % self._name,
                    "sku": "[variables('imgSku_%s')]" % self._name,
                    "version": "latest"
                },
                "osDisk": {
                    "name": "osdisk",
                    "vhd": {
                        "uri": "[concat('http://',"
                               "parameters('newStorageAccountName'),"
                               "'.blob.core.windows.net/',variables("
                               "'vmStorageAccountContainerName'),'/',"
                               "variables('vmName_%s'),'_root.vhd')]" %
                               self._name
                    },
                    "caching": "ReadWrite",
                    "createOption": "FromImage"
                }
            },
            "networkProfile": {
                "networkInterfaces": self._get_network_interfaces()
            }
        }

    def get_parameters(self):
        """ get_parameters returns the dict of ARM template parameters
        associated with the Heat template's translation.
        """
        return {
            "adminUsername": {
                "type": "string",
                "metadata": {
                    "description": "User name for the Virtual Machine."
                }
            },
            "adminPassword": {
                "type": "securestring",
                "metadata": {
                    "description": "Password for the Virtual Machine."
                }
            },
        }

    def get_dependencies(self):
        """ get_dependencies returns the list of resources which are required
        by this resource.
        """
        depends_on = [
            "[concat('Microsoft.Storage/storageAccounts/', "
            "parameters('newStorageAccountName'))]"
        ]

        for port_resource_name in self._get_ref_port_resource_names():
            depends_on.append(
                "[concat('Microsoft.Network/networkInterfaces/', "
                "variables('nicName_%s'))]" % port_resource_name)

        return depends_on

    def get_resource_data(self):
        resource_data = [{
            "apiVersion": constants.ARM_API_2015_05_01_PREVIEW,
            "type": self.arm_resource_type,
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
            "location": "[variables('location')]",
            "properties": self._get_vm_properties(),
            "dependsOn": self.get_dependencies(),
        }]

        return resource_data
