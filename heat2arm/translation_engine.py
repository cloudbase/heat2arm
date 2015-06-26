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
from heat2arm.translators import neutron
from heat2arm.translators import novaserver

opts = [
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
]

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.register_opts(opts)

DEFAULT_STORAGE_ACCOUNT_CONTAINER_NAME = "vhds"

RESOURCE_TRANSLATORS = [
    novaserver.NovaServerARMTranslator,
    neutron.NeutronNetARMTranslator,
    neutron.NeutronSubnetARMTranslator,
    neutron.NeutronPortARMTranslator,
    neutron.NeutronFloatingIPARMTranslator,
    neutron.NeutronRouterARMTranslator,
    neutron.NeutronRouterInterfaceARMTranslator
    ]


def validate_template_data(template_data):
    schema = get_arm_schema()
    jsonschema.validate(template_data, schema)


def get_resource_translator(heat_resource):
    rt = [rt for rt in RESOURCE_TRANSLATORS if
          rt.heat_resource_type == heat_resource.type()]

    if rt:
        return rt[0](heat_resource)
    else:
        LOG.warn('Could not find a corresponding ARM resource for Heat '
                 'resource "%s"' % heat_resource.type())


def get_arm_schema():
    response = requests.get(constants.ARM_SCHEMA_URL)
    response.raise_for_status()
    return json.loads(response.text)


def get_arm_template(resources, location=CONF.default_azure_location):
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
    t = template.Template(heat_template_data)
    t.validate()

    ctx = test_utils.dummy_context()

    s = stack.Stack(context=ctx, stack_name="Dummy", tmpl=t)
    t.validate_resource_definitions(s)

    arm_resources = []
    for heat_resource in s.iter_resources():
        rt = get_resource_translator(heat_resource)
        if rt:
            arm_resources.append(rt)

    arm_template_data = get_arm_template(arm_resources)
    if CONF.validate_arm_template_schema:
        validate_template_data(arm_template_data)

    return arm_template_data
