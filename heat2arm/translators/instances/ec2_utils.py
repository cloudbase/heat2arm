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
    This module contains definitions for a handful of helper functions
    which aid in instance translations.
"""

from oslo.config import cfg

# Get the config instance and add options:
CONF = cfg.CONF
CONF.register_opts({
    cfg.DictOpt(
        "ec2_vm_type_to_size_map",
        default={
            "m1.tiny": "Basic_A0",
            "m1.small": "Basic_A1",
            "m1.medium": "Basic_A2",
            "m1.large": "Basic_A3",
            "m1.xlarge": "basic_A4",
        },
        help="A mapping between EC2 VM types and Azure machine sizes."
    ),
    cfg.DictOpt(
        "ec2_vm_image_map",
        default={
            "U10-x86_64-cfntools":
            "Canonical;UbuntuServer;12.04.5-LTS"
        },
        help="A map between EC2 image names and Azure ones.",
    )
})


def get_azure_flavor(flavor):
    """ get_azure_flavor is a helper function which returns the
    appropriate Azure VM size corresponding to the given Amazon
    image flavor or a the pre-set sensible default.
    """
    return CONF.ec2_vm_type_to_size_map.get(flavor, CONF.vm_default_size)


def get_azure_image_info(ec2_image):
    """ get_azure_image_info is a helper function which returns
    the info of the image.
    """
    azure_image_info_str = CONF.ec2_vm_image_map.get(ec2_image)
    if not azure_image_info_str:
        raise Exception(
            'Nova image "%s" cannot be mapped to an Azure equivalent. Please '
            'update the "ec2_vm_image_map" configuration option' % ec2_image)

    azure_image_info = tuple(azure_image_info_str.split(";"))
    if len(azure_image_info) != 3:
        raise Exception(
            '"%s" does not contain valid Azure image data. The required '
            'format is "publisher;offer;sku"')

    return azure_image_info
