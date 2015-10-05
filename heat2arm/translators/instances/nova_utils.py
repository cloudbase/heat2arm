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

from heat2arm.config import CONF


def get_azure_flavor(flavor):
    """ get_azure_flavor is a helper function which returns the
    appropriate Azure VM size corresponding to the given image flavor
    or a the pre-set sensible default.
    """
    if flavor not in CONF.nova_flavor_to_size_map:
        raise Exception("Could not find mapping for the EC2 image size "
                        "'%s', please edit 'nova_flavor_to_size_map' in the "
                        "configuration." % flavor)

    return CONF.nova_flavor_to_size_map[flavor]


def get_azure_image_info(nova_image):
    """ get_azure_image_info is a helper function which returns
    the info of the image.
    """
    azure_image_info_str = CONF.nova_vm_image_map.get(nova_image, None)

    if not azure_image_info_str:
        raise Exception(
            'Nova image "%s" cannot be mapped to an Azure equivalent. Please '
            'update the "CONF.nova_vm_image_map" configuration option' %
            nova_image)

    azure_image_info = tuple(azure_image_info_str.split(";"))
    if len(azure_image_info) != 3:
        raise Exception(
            '"%s" does not contain valid Azure image data. The required '
            'format is "publisher;offer;sku"')

    return azure_image_info
