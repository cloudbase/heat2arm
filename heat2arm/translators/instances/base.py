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

from heat2arm.constants import ARM_API_2015_05_01_PREVIEW
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseInstanceARMTranslator(BaseHeatARMTranslator):
    """ BaseInstanceARMTranslator is a specialised version of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to facilitate iiheriting instance translators.
    """
    def get_parameters(self):
        """ get_parameters is a sensible override of the method of the Base
        translator for fetching the parameters of the ARM translation.

        It returns a dict containing a user name and password parameters.
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

    def _get_base_vm_header(self):
        """ _get_base_vm_header is a helper method which returns a dict
        containing the standard set of properties of an ARM VM declaration.
        """
        return {
            "apiVersion": ARM_API_2015_05_01_PREVIEW,
            "type": self.arm_resource_type,
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
            "location": "[variables('location')]",
        }

    def _get_base_os_profile_data(self):
        """ _get_base_os_profile_data is helper method which returns
        the default OS profile information.
        """
        return {
            "computername": "[variables('vmName_%s')]" % self._name,
            "adminUsername": "[parameters('adminUsername')]",
            "adminPassword": "[parameters('adminPassword')]",
        }

    def _get_base_vm_properties(self):
        """ _get_base_vm_properties is a helper method which returns a default
        dict of properties that all ARM template VM definitions should contain.

        There are still some specific options which require specialised
        per-translator identifying, such as networking options.
        """
        return {
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
        }
