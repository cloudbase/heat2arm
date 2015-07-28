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
from heat2arm.translators import global_constants


class BaseInstanceARMTranslator(BaseHeatARMTranslator):
    """ BaseInstanceARMTranslator is a specialised version of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to facilitate inheriting instance translators.
    """
    arm_resource_type = "Microsoft.Compute/virtualMachines"

    def __init__(self, heat_resource):
        global_constants.NEW_STORAGE_ACC_REQUIRED = True
        super(BaseInstanceARMTranslator, self).__init__(heat_resource)

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
        base_vars = {
            self._make_var_name("vmName"): self._name,
        }

        # check if we need to add a variable for the network interface we may
        # need to later create for the VM:
        if not self._get_network_interfaces():
            base_vars.update({
                "nicName_VM_%s" % self._name: "nic_VM_%s" % self._name,
            })

        return base_vars

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_names is a helper method which returns a
        list of all the Neutron port resource names which either are referenced
        by a Nova server or reference an EC2 instance.

        NOTE: it is stubbed and should be implemented by inheriting classes.
        """
        pass

    def _get_attached_volumes(self):
        """ _get_attached_volumes is a helper function which returns the list
        of all volumes attached to the instance.

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

        # add any attached volumes, if applicable:
        volumes = self._get_attached_volumes()
        if volumes:
            vm_properties["storageProfile"].update({
                "dataDisks": volumes
            })

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
        network_interfaces = self._get_network_interfaces()
        if network_interfaces:
            # specify the found interfaces:
            vm_properties["networkProfile"].update({
                "networkInterfaces": self._get_network_interfaces(),
            })
        else:
            # else; add the default virtual network we will create later:
            vm_properties["networkProfile"].update({
                "networkInterfaces": [{
                    "id": "[resourceId('Microsoft.Network/networkInterfaces', "
                          "variables('nicName_VM_%s'))]" % self._name
                }]
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

        # check if there are any network interfaces already defined to add:
        for port_resource_name in self._get_ref_port_resource_names():
            depends_on.append(
                "[concat('Microsoft.Network/networkInterfaces/', "
                "variables('nicName_%s'))]" % port_resource_name)

        # else, add the default one which will be specially created for the VM:
        if not self._get_network_interfaces():
            depends_on.extend([
                "[concat('Microsoft.Network/virtualNetworks/', "
                "parameters('newVirtualNetworkName'))]",
                "[concat('Microsoft.Network/networkInterfaces/', "
                "variables('nicName_VM_%s'))]" % self._name,
            ])

        return depends_on

    def get_resource_data(self):
        """ get_resource_data returns a list of all the options associated to
        this resource which is directly serializable into JSON and used in the
        resulting ARM template for this resource.
        """
        resource_data = [{
            "apiVersion": ARM_API_VERSION,
            "type": self.arm_resource_type,
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
            "location": "[variables('location')]",
            "properties": self._get_vm_properties(),
            "dependsOn": self.get_dependencies(),
        }]

        # if the VM has no previously-defined network interfaces;
        # add a new one to link it to the default network:
        if not self._get_network_interfaces():
            global_constants.NEW_VIRTUAL_NETWORK_REQUIRED = True
            resource_data.extend([
                {
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
                }])

        return resource_data
