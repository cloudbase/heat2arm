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

import json
import logging

from heat2arm.config import CONF


LOG = logging.getLogger("__heat2arm__.context")


class Context(object):
    """ Context represents the specific context of the ongoing translation.
    It holds and provides access to all already declared parameters, variables
    and resources, as well as some important aspects to be kept in mind
    regarding the current translation (ex: should a default storage account be
    created to support the translated deployment).
    """
    def __init__(self, heat_resource_stack):
        """ A Context object is created from the full Heat resource stack
        (simply a dict of resource names to resource data mappings).
        """
        self.heat_resource_stack = heat_resource_stack
        self.heat_resources = heat_resource_stack.values()

        self.parameters = {}
        self.variables = {
            "location": CONF.azure_location
        }
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

    def __str__(self):
        """ __str__ simply returns the name of the class. """
        return self.__class__.__name__

    def get_template_data(self):
        """ get_template_data returns all the data stored so far to be
        directly serialized into the resulting template.
        """
        if self.__new_storage_acc_required:
            LOG.warning("'context': addition of an extra storage account is "
                        "required for supporting the deployment.")
            self.__set_storage_account_resource()

        if self.__new_virtual_network_required:
            LOG.warning("'context': addition of an extra virtual network is "
                        "required for supporting the deployment.")
            self.__set_virtual_network_resource()

        return {
            "parameters": self.parameters,
            "variables": self.variables,
            "resources": self.resources,
        }

    def add_parameters(self, parameters):
        """ add_parameters adds the given parameters to the context.
        """
        LOG.debug(
            "'%s': adding parameters: %s",
            self, json.dumps(parameters, indent=4)
        )
        self.parameters.update(parameters)

    def add_variables(self, variables):
        """ add_variables adds the given dict of variables to the context.
        """
        LOG.debug(
            "'%s': adding variables: %s", self,
            json.dumps(variables, indent=4)
        )
        self.variables.update(variables)

    def add_resource(self, resource):
        """ add_resource adds a resource to the context's resources.
        """
        LOG.debug(
            "'%s': adding resource: %s", self,
            json.dumps(resource, indent=4)
        )
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

    def get_arm_resource(self, resource_props):
        """ get_arm_resource returns the dict of the existing ARM resource
        which matches the provided properties.
        """
        LOG.debug(
            "'%s': asked to fetch arm resource matching: %s",
            self, json.dumps(resource_props, indent=4)
        )

        for res in self.resources:
            if all((k in res and res[k] == v) for k, v in
                   resource_props.items()):
                LOG.debug(
                    "'%s': found arm resource: %s",
                    self, json.dumps(res, indent=4)
                )
                return res

    def get_heat_resources(self, resource_props):
        """ get_heat_resources returns the list of all Heat resource present in
        the template which satisfy the provided properties.
        """
        LOG.debug(
            "'%s': asked to fetch heat resources matching: %s",
            self, json.dumps(resource_props, indent=4)
        )

        resources = []

        for res in self.heat_resources:
            props = res.properties
            if all((k in props and props[k] == v) for k, v in
                   resource_props.items()):
                resources.append(res)

        LOG.debug(
            "'%s': found heat resources: %s",
            self, json.dumps(resources, indent=4)
        )

        return resources

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
            'storageAccountType': CONF.azure_storage_account_type,
            "vmStorageAccountContainerName":
                CONF.azure_storage_container_name
        })

        self.resources.append({
            "type": "Microsoft.Storage/storageAccounts",
            "name": "[parameters('newStorageAccountName')]",
            "apiVersion": CONF.arm_api_version,
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
                                   " for supporting this deployment."
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
            "apiVersion": CONF.arm_api_version,
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
