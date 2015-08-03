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
import json
import jsonschema
import logging
import requests

from oslo_config import cfg

from heat.engine import stack
from heat.engine import template
from heat.tests import utils as test_utils

from heat2arm import constants
from heat2arm.context import Context
from heat2arm.translators import instances
from heat2arm.translators import networking
from heat2arm.translators import storage


LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.register_opts([
    cfg.StrOpt(
        'default_azure_location',
        default=constants.DEFAULT_LOCATION,
        help='Default Azure location'),
    cfg.StrOpt(
        'default_azure_storage_account_type',
        default=constants.DEFAULT_STORAGE_ACCOUNT_TYPE,
        choices=["Standard_LRS",
                 "Standard_ZRS",
                 "Standard_GRS",
                 "Standard_RAGRS",
                 "Premium_LRS"],
        help='Default Azure storage account type'),
    cfg.StrOpt(
        'default_storage_container_name',
        default=constants.DEFAULT_STORAGE_CONTAINER_NAME,
        help='Default name of the storage container.'
    ),
    cfg.BoolOpt(
        'validate_arm_template_schema',
        default=False,
        help='Validate the generated ARM template schema'),
])

CTX = Context(CONF.default_azure_location)

RESOURCE_TRANSLATORS = [
    instances.NovaServerARMTranslator,
    instances.EC2InstanceARMTranslator,
    networking.EC2SecurityGroupARMTranslator,
    networking.NeutronSecurityGroupARMTranslator,
    networking.NeutronRouterARMTranslator,
    networking.NeutronRouterInterfaceARMTranslator,
    networking.EC2eipARMTranslator,
    networking.NeutronFloatingIPARMTranslator,
    networking.NeutronNetARMTranslator,
    networking.NeutronSubnetARMTranslator,
    networking.EC2eipAssocARMTranslator,
    networking.NeutronPortARMTranslator,
    storage.CinderVolumeARMTranslator,
    storage.CinderVolumeAttachmentARMTranslator,
    storage.EBSVolumeARMTranslator,
    storage.EBSVolumeAttachmentARMTranslator,
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
    res_trans = None
    for trans in RESOURCE_TRANSLATORS:
        if trans.heat_resource_type == heat_resource.type():
            res_trans = trans

    if res_trans:
        return res_trans(heat_resource, CTX)
    else:
        LOG.warn('Could not find a corresponding ARM resource for Heat '
                 'resource "%s"', heat_resource.type())


def get_arm_schema():
    """ get_arm_schema fetches the ARM schema from its default URL. """
    response = requests.get(constants.ARM_SCHEMA_URL)
    response.raise_for_status()
    return json.loads(response.text)


def get_arm_template(resources):
    """ get_arm_template takes a list of resources and returns a dict which is
    directly renderable into the JSON of an ARM template.
    """
    # run each resource translator:
    for resource in resources:
        resource.translate()

    # also, let all the resource translators apply any changes
    # to the context they require:
    for resource in resources:
        resource.update_context()

    template_data = CTX.get_template_data()
    template_data.update({
        "$schema": constants.ARM_SCHEMA_URL,
        "contentVersion": constants.ARM_TEMPLATE_VERSION
    })

    return collections.OrderedDict([
        ("contentVersion", constants.ARM_TEMPLATE_VERSION),
        ("$schema", constants.ARM_SCHEMA_URL),
        ("parameters", template_data["parameters"]),
        ("variables", template_data["variables"]),
        ("resources", template_data["resources"])
    ])


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
