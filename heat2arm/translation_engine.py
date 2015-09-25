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
    This module contains the main logic of the translation engine.
"""

import collections
import json
import jsonschema
import logging
import requests

from heat2arm.config import CONF
from heat2arm.context import Context
from heat2arm.parser.parsing import parse_template
from heat2arm.translators import autoscaling
from heat2arm.translators import instances
from heat2arm.translators import networking
from heat2arm.translators import storage


LOG = logging.getLogger("__heat2arm__")

# RESOURCE_TRANSLATORS is a list of all the resource translator
# classes to be used within the translation process.
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
    autoscaling.AWSAutoScalingGroupARMTranslator,
    autoscaling.AWSScalingPolicyARMTranslator,
    autoscaling.AWSLaunchConfigurationARMTranslator
]


def validate_template_data(template_data):
    """ validate_template_data validates the given template against the ARM
    schema obtained through calling get_arm_schema.
    """
    schema = get_arm_schema()
    jsonschema.validate(template_data, schema)


def get_resource_translator(heat_resource, context):
    """ get_resource_translator runs through all the available trainslators and
    finds the appropriate one for the given heat resource type or logs a
    warning message if no translator is available.
    """
    res_trans = None
    for trans in RESOURCE_TRANSLATORS:
        # TODO
        if trans.heat_resource_type == heat_resource.type:
            res_trans = trans

    if res_trans:
        return res_trans(heat_resource, context)
    else:
        LOG.warn('Could not find a corresponding ARM resource for Heat '
                 'resource "%s"', heat_resource.type)


def get_arm_schema():
    """ get_arm_schema fetches the ARM schema from its default URL. """
    response = requests.get(CONF.arm_schema_url)
    response.raise_for_status()
    return json.loads(response.text)


def get_arm_template(resources, context):
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

    template_data = context.get_template_data()

    return collections.OrderedDict([
        ("contentVersion", CONF.arm_template_version),
        ("$schema", CONF.arm_schema_url),
        ("parameters", template_data["parameters"]),
        ("variables", template_data["variables"]),
        ("resources", template_data["resources"])
    ])


def convert_template(heat_template_data):
    """ convert_template takes a heat template and converts it into an ARM
    template.
    """
    heat_stack = parse_template(heat_template_data)

    context = Context(heat_stack)

    arm_resources = []
    for heat_resource in heat_stack.values():
        res_trans = get_resource_translator(heat_resource, context)
        if res_trans:
            arm_resources.append(res_trans)

    arm_template_data = get_arm_template(arm_resources, context)
    if CONF.validate_arm_template_data:
        validate_template_data(arm_template_data)

    return arm_template_data
