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
    Defines class which encompasses common functionality for
    both Nova and EC2 instance translators.
"""

import json

from heat2arm.constants import ARM_API_VERSION
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseInstanceARMTranslator(BaseHeatARMTranslator):
    """ BaseInstanceARMTranslator is a specialised version of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to facilitate inheriting instance translators.
    """
    arm_resource_type = "Microsoft.Compute/virtualMachines"

    def __init__(self, heat_resource, context):
        super(BaseInstanceARMTranslator, self).__init__(heat_resource, context)
        self._context.set_storage_account_required()

    def get_parameters(self):
        """ get_parameters is a sensible override of the method of the Base
        translator for fetching the parameters of the ARM translation.

        It returns a dict containing a user name and password parameters, and
        optionally the paramters for a VN and subnet if one is required.
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
            }
        }

    def _get_base_variables(self):
        """ _get_base_variables is a helper method which retuns the list of
        variables all instance translations require.
        """
        return {
            self._make_var_name("vmName"): self._name,
        }

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_names is a helper method which returns a
        list of all the Neutron port resource names which either are referenced
        by a Nova server or reference an EC2 instance.

        NOTE: it is stubbed and should be implemented by inheriting classes.
        """
        pass

    def _get_userdata(self):
        """ _get_userdata is a helper method which returns the userdata from
        the instance's definition, if any.

        NOTE: it is stubbed and should be implemented by inheriting classes.
        """
        pass

    def _get_network_interfaces(self):
        """ _get_network_interfaces is a helper method which returns a list of
        all the network interfaces which are attached to this Nova server.
        """
        network_interfaces_data = []

        for port_resource_name in self._get_ref_port_resource_names():
            network_interfaces_data.append({
                "id": "[resourceId('Microsoft.Network/networkInterfaces', "
                      "variables('nicName_%s'))]" % port_resource_name
            })

        if not network_interfaces_data:
            self._context.set_virtual_network_required()

        return network_interfaces_data

    def _get_base_os_profile_data(self):
        """ _get_base_os_profile_data is helper method which returns
        the default OS profile information.
        """
        return {
            "computername": "[variables('vmName_%s')]" % self._name,
            "adminUsername": "[parameters('adminUsername')]",
            "adminPassword": "[parameters('adminPassword')]",
        }

    def _get_vm_properties(self):
        """ _get_vm_properties is a helper method which returns the dict of all
        auxiliary properties of the instance.
        """
        # list the properties all instances must have:
        vm_properties = {
            "hardwareProfile": {
                "vmSize": "[variables('vmSize_%s')]" % self._name
            },
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
            "networkProfile": {},
        }

        # add the userData:
        os_profile_data = self._get_base_os_profile_data()

        user_data = self._get_userdata()
        if user_data:
            os_profile_data["customData"] = (
                "[base64('%s')]" % json.dumps(user_data))

        vm_properties.update({
            "osProfile": os_profile_data,
        })

        # add the network interface(s):
        vm_properties["networkProfile"].update({
            "networkInterfaces": self._get_network_interfaces(),
        })

        return vm_properties

    def get_dependencies(self):
        """ get_dependencies returns the list of resources which are
        required by this resource.
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
        return {
            "apiVersion": ARM_API_VERSION,
            "type": self.arm_resource_type,
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
            "location": "[variables('location')]",
            "properties": self._get_vm_properties(),
            "dependsOn": self.get_dependencies(),
        }

    def update_context(self):
        """ update_context updates the context to add the necessary parameters,
        variables and resource data required for the definition of the
        networkInterface required to attach this VM to the default VN (if
        applicable).
        """
        if self._get_network_interfaces():
            # nothing to do; can return now:
            return

        self._context.add_variables({
            "nicName_VM_%s" % self._name: "nic_VM_%s" % self._name,
        })

        res = self._context.get_resource({
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
            "type": self.arm_resource_type
        })

        # add the default VN and the NIC as dependencies:
        res["dependsOn"].extend([
            "[concat('Microsoft.Network/virtualNetworks/', "
            "parameters('newVirtualNetworkName'))]",
            "[concat('Microsoft.Network/networkInterfaces/', "
            "variables('nicName_VM_%s'))]" % self._name
        ])

        res["properties"]["networkProfile"].update({
            "networkInterfaces": [{
                "id": "[resourceId('Microsoft.Network/networkInterfaces', "
                      "variables('nicName_VM_%s'))]" % self._name
            }]
        })

        self._context.add_resource({
            "name": "[variables('nicName_VM_%s')]" % self._name,
            "apiVersion": ARM_API_VERSION,
            "location": "[variables('location')]",
            "type": "Microsoft.Network/networkInterfaces",
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworks/', "
                "parameters('newVirtualNetworkName'))]"
            ],
            "properties": {
                "ipConfigurations": [{
                    "name": "ipConfig_nic_VM_%s" % self._name,
                    "properties": {
                        "subnet": {
                            "id": "[variables('defaultSubnetRef')]"
                        },
                        "privateIPAllocationMethod": "Dynamic",
                    }
                }]
            }
        })
