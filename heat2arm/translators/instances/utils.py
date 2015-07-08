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


def get_azure_flavor(conf, flavor):
    """ get_azure_flavor is a helper funcion which returns the
    appropriate Azure VM size corresponding to the given image flavor
    or a the pre-set sensible default.

    conf: oslo_config.cfg.ConfigOpts.

    It relies on options called 'vm_flavor_size_map' and 'vm_default_size'
    having been pre-set in the conf.
    """
    return conf.vm_flavor_size_map.get(flavor, conf.vm_default_size)


def get_azure_image_info(conf, nova_image):
    """ get_azure_image_info is a helper function which returns
    the info of the image.

    conf: oslo_config.cfg.ConfigOpts.

    It relies on options called 'vm_image_map'
    having been pre-set in the conf.
    """
    azure_image_info_str = conf.vm_image_map.get(nova_image)
    if not azure_image_info_str:
        raise Exception(
            'Nova image "%s" cannot be mapped to an Azure equivalent. Please '
            'update the "vm_image_map" configuration option' % nova_image)

    azure_image_info = tuple(azure_image_info_str.split(";"))
    if len(azure_image_info) != 3:
        raise Exception(
            '"%s" does not contain valid Azure image data. The required '
            'format is "publisher;offer;sku"')

    return azure_image_info
