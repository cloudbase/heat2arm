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
    Contains all the basic layout of the translation engine.
"""

import collections
import logging

import json
import jsonschema
import requests

from oslo_config import cfg

from heat.engine import stack
from heat.engine import template
from heat.tests import utils as test_utils

from heat2arm import constants
from heat2arm.translators import instances
from heat2arm.translators import networking


LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.register_opts([
    cfg.StrOpt(
        'default_azure_location',
        default="West US",
        help='Default Azure location'),
    cfg.StrOpt(
        'default_azure_storage_account_type',
        default="Standard_LRS",
        choices=["Standard_LRS",
                 "Standard_ZRS",
                 "Standard_GRS",
                 "Standard_RAGRS",
                 "Premium_LRS"],
        help='Default Azure storage account type'),
    cfg.BoolOpt(
        'validate_arm_template_schema',
        default=False,
        help='Validate the generated ARM template schema'),
])

DEFAULT_STORAGE_ACCOUNT_CONTAINER_NAME = "vhds"

RESOURCE_TRANSLATORS = [
    instances.NovaServerARMTranslator,
    instances.EC2InstanceARMTranslator,
    networking.EC2SecurityGroupARMTranslator,
    networking.NeutronSecurityGroupARMTranslator,
    networking.NeutronRouterARMTranslator,
    networking.NeutronRouterInterfaceARMTranslator,
    networking.NeutronFloatingIPARMTranslator,
    networking.NeutronNetARMTranslator,
    networking.NeutronSubnetARMTranslator,
    networking.NeutronPortARMTranslator,
]


def validate_template_data(template_data):
    """ validate_template_data validates the given template against the ARM
    schema obtained through calling get_arm_schema.
    """
    schema = get_arm_schema()
    jsonschema.validate(template_data, schema)


def get_resource_translator(heat_resource):
    """ get_resource_translator runs through all the available trainslators and
    finds the appropriate one for the given heat resource type or logs a
    warning message if no translator is available.
    """
    res_trans = [rt for rt in RESOURCE_TRANSLATORS if
                 rt.heat_resource_type == heat_resource.type()]

    if res_trans:
        return res_trans[0](heat_resource)
    else:
        LOG.warn('Could not find a corresponding ARM resource for Heat '
                 'resource "%s"', heat_resource.type())


def get_arm_schema():
    """ get_arm_schema fetches the ARM schema from its default URL. """
    response = requests.get(constants.ARM_SCHEMA_URL)
    response.raise_for_status()
    return json.loads(response.text)


def get_arm_template(resources, location=CONF.default_azure_location):
    """ get_arm_template takes a list of resources and returns a dict which is
    directly renderable into the JSON of an ARM template.
    """
    parameters_data = collections.OrderedDict()
    variables_data = collections.OrderedDict({
        "location": location,
        "vmStorageAccountContainerName": DEFAULT_STORAGE_ACCOUNT_CONTAINER_NAME
    })
    resources_data = []

    # This is the storage for local disks, there's no OpenStack equivalent
    (storage_parameters,
     storage_variables,
     storage_resource) = get_storage_account_resource()

    parameters_data.update(storage_parameters)
    variables_data.update(storage_variables)
    resources_data.append(storage_resource)

    for resource in resources:
        variables_data.update(resource.get_variables())
        resources_data += resource.get_resource_data()
        parameters_data.update(resource.get_parameters())

    template_data = {
        "$schema": constants.ARM_SCHEMA_URL,
        "contentVersion": "1.0.0.0",
        "parameters": parameters_data,
        "variables": variables_data,
        "resources": resources_data,
    }

    return template_data


def get_storage_account_resource():
    """ get_storage_account_resource returns the
    (parameters, variables, resource) touple associated to the storage account
    which will be created on Azure for any storage-related operations.
    """
    parameters = {
        "newStorageAccountName": {
            "type": "string",
            "metadata": {
                "description": "Unique DNS Name for the Storage Account where "
                               "the Virtual Machine's disks will be placed."
            }
        },
    }

    variables = {
        'storageAccountType': CONF.default_azure_storage_account_type,
    }

    resource = {
        "type": "Microsoft.Storage/storageAccounts",
        "name": "[parameters('newStorageAccountName')]",
        "apiVersion": constants.ARM_API_2015_05_01_PREVIEW,
        "location": "[variables('location')]",
        "properties": {
            "accountType": "[variables('storageAccountType')]"
        }
    }

    return (parameters, variables, resource)


def convert_template(heat_template_data):
    """ convert_template takes a heat template and converts it into an ARM
    template.
    """
    temp = template.Template(heat_template_data)
    temp.validate()

    ctx = test_utils.dummy_context()

    heat_stack = stack.Stack(context=ctx, stack_name="Dummy", tmpl=temp)
    temp.validate_resource_definitions(heat_stack)

    arm_resources = []
    for heat_resource in heat_stack.iter_resources():
        res_trans = get_resource_translator(heat_resource)
        if res_trans:
            arm_resources.append(res_trans)

    arm_template_data = get_arm_template(arm_resources)
    if CONF.validate_arm_template_schema:
        validate_template_data(arm_template_data)

    return arm_template_data
