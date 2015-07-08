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

from heat2arm.translators.instances.base import BaseInstanceARMTranslator
from heat2arm.translators.instances import utils

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
    cfg.DictOpt(
        'vm_image_map',
        default={
            'ubuntu.12.04.LTS.x86_64':
            "Canonical;UbuntuServer;12.04.5-LTS",
        },
        help='A map between OpenStack Nova and Azure VM images'),
])


class NovaServerARMTranslator(BaseInstanceARMTranslator):
    """ NovaServerARMTranslator is the translator associated to a Nova server.

    It processes the fields and parameters of a Nova server defined in Heat.
    """
    heat_resource_type = "OS::Nova::Server"
    arm_resource_type = "Microsoft.Compute/virtualMachines"

    def get_variables(self):
        """ get_variables returns the dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        (publisher, offer, sku) = utils.get_azure_image_info(
            CONF, self._heat_resource.properties['image'])

        return {
            "vmName_%s" % self._name: self._name,
            "vmSize_%s" % self._name: utils.get_azure_flavor(
                CONF, self._heat_resource.properties['flavor']),
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
        os_profile_data = self._get_base_os_profile_data()

        user_data = self._heat_resource.properties['user_data']
        if user_data:
            os_profile_data["customData"] = (
                "[base64('%s')]" % json.dumps(user_data))

        vm_properties = self._get_base_vm_properties()
        vm_properties.update({
            "osProfile": os_profile_data,
            "networkProfile": {
                "networkInterfaces": self._get_network_interfaces()
            }
        })

        return vm_properties

    # NOTE: get_parameters is inherited from BaseInstanceARMTranslator.

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
        """ get_resource_data returns a list of all the options associated to
        this resource which is directly serializable into JSON and used in the
        resulting ARM template for this resource.
        """
        resource_data = self._get_base_vm_header()
        resource_data.update({
            "properties": self._get_vm_properties(),
            "dependsOn": self.get_dependencies(),
        })

        return [resource_data]
