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
    Defines the main translation context which will give resource translators
    the ability to read, update and delete parameters, variables and resources
    which have already been declared.
"""

from oslo_config import cfg

from heat2arm import constants


class Context(object):
    """ Context represents the specific context of the ongoing translation.
    It holds and provides access to all already declared parameters, variables
    and resources, as well as some important aspects to be kept in mind.
    """
    def __init__(self, location=constants.DEFAULT_LOCATION):
        self.parameters = {}
        self.variables = {}
        self.resources = []

        # availability_set_names is a list of the names of availability sets
        # registered so far to exist. It is necessary due to the fact that it
        # is mostly the translator's jobs to add new ones if necessary.
        self.availability_set_names = []

        # new_storage_acc_required signals whether a new storage account should
        # be created in order to support any storage-related operations.
        self.__new_storage_acc_required = False

        # new_virtual_network_required specifies whether a new virtual network
        # is required to be created for the deployment
        self.__new_virtual_network_required = False

        self.variables["location"] = location

    def get_template_data(self):
        """ get_template_data returns all the data stored so far to be
        directly serialized into the resulting template.
        """
        if self.__new_storage_acc_required:
            self.__set_storage_account_resource()

        if self.__new_virtual_network_required:
            self.__set_virtual_network_resource()

        return {
            "parameters": self.parameters,
            "variables": self.variables,
            "resources": self.resources,
        }

    def add_parameters(self, parameters):
        """ add_parameters adds the given parameters to the context.
        """
        self.parameters.update(parameters)

    def add_variables(self, variables):
        """ add_variables adds the given dict of variables to the context.
        """
        self.variables.update(variables)

    def add_resource(self, resource):
        """ add_resource adds a resource to the context's resources.
        """
        self.resources.append(resource)

    def set_storage_account_required(self):
        """ set_storage_account_required sets the
        __new_storage_acc_required flag.
        """
        self.__new_storage_acc_required = True

    def set_virtual_network_required(self):
        """ set_virtual_network_required sets the
        __new_virtual_network_required flag.
        """
        self.__new_virtual_network_required = True

    def get_resource(self, resource):
        """ get_resource returns the dict of the resource which matches the
        given fields.
        """
        for res in self.resources:
            if all((k in res and res[k] == v) for k, v in
                   resource.items()):
                return res

    def __set_storage_account_resource(self):
        """ __set_storage_account_resource is a helper method which sets the
        parameters, variables and resource data for the default storage account
        to be used for all storage-related operations.
        """
        self.parameters.update({
            "newStorageAccountName": {
                "type": "string",
                "metadata": {
                    "description": "Unique DNS Name for the Storage Account to"
                                   " be used for the deployment."
                }
            },
        })

        self.variables.update({
            'storageAccountType': cfg.CONF.default_azure_storage_account_type,
            "vmStorageAccountContainerName":
                cfg.CONF.default_storage_container_name,
        })

        self.resources.append({
            "type": "Microsoft.Storage/storageAccounts",
            "name": "[parameters('newStorageAccountName')]",
            "apiVersion": constants.ARM_API_VERSION,
            "location": "[variables('location')]",
            "properties": {
                "accountType": "[variables('storageAccountType')]"
            }
        })

    def __set_virtual_network_resource(self):
        """ __set_virtual_network_resource is a helper method which sets the
        parameters, variables and resource data for the default virtual network
        to be used to support the deployment.
        """
        self.parameters.update({
            "newVirtualNetworkName": {
                "type": "string",
                "metadata": {
                    "description": "Name of the Virtual Network to be created"
                                   "for this deployment."
                }
            }
        })

        self.variables.update({
            "newVirtualNetworkRef": "[resourceId('Microsoft.Network"
                                    "/virtualNetworks', parameters("
                                    "'newVirtualNetworkName'))]",
            "defaultSubnetName": "defaultVNSubnet",
            "defaultSubnetRef": "[concat(variables('newVirtualNetworkRef'),"
                                "'/subnets/',variables('defaultSubnetName'))]"
        })

        self.resources.append({
            "type": "Microsoft.Network/virtualNetworks",
            "name": "[parameters('newVirtualNetworkName')]",
            "apiVersion": constants.ARM_API_VERSION,
            "location": "[variables('location')]",
            "properties": {
                "subnets": [{
                    "name": "[variables('defaultSubnetName')]",
                    "properties": {
                        "addressPrefix": "10.0.0.0/24"
                    }
                }],
                "addressSpace": {
                    "addressPrefixes": [
                        "10.0.0.0/24"
                    ]
                }
            },
        })
