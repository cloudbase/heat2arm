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
    Defines the translator and auxiliary functions for EC2 instances.
"""

import json
import logging

from oslo_config import cfg

from heat2arm.translators.instances import utils
from heat2arm.translators.instances.base_instance import (
    BaseInstanceARMTranslator
)


LOG = logging.getLogger(__name__)

# Get the config instance and add options:
CONF = cfg.CONF
CONF.register_opts({
    cfg.DictOpt(
        "vm_type_to_size_map",
        # TODO: would be nice to be able to auto-generate these:
        default={
            "m1.tiny": "Basic_A0",
            "m1.small": "Basic_A1",
            "m1.medium": "Basic_A2",
            "m1.large": "Basic_A3",
            "m1.xlarge": "basic_A4",
        },
        help="A mapping between EC2 VM types and Azure machine sizes."
    ),
    cfg.StrOpt(
        "vm_default_size",
        default="Basic_A1",
        help="Default Azure size in case of an EC2 VM type "
             "could not be mapped.",
    ),
    cfg.DictOpt(
        "vm_image_map",
        default={
            "U10-x86_64-cfntools":
            "Canonical;UbuntuServer;10.04-LTS"
        },
        help="A map between EC2 image names and Azure ones.",
    )
})


class EC2InstanceARMTranslator(BaseInstanceARMTranslator):
    """ EC2InstanceARMTranslator is the translator associated to an EC2
    instance.
    """
    heat_resource_type = "AWS::EC2::Instance"

    def get_variables(self):
        """ get_variables returns a dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        (publisher, offer, sku) = utils.get_azure_image_info(
            CONF, self._heat_resource.properties["InstanceType"]
        )

        return {
            self._make_var_name("vmName"): self._name,
            self._make_var_name("vmSize"): utils.get_azure_flavor(
                CONF, self._heat_resource.properties["InstanceType"]
            ),
            self._make_var_name("imgPublisher"): publisher,
            self._make_var_name("imgOffer"): offer,
            self._make_var_name("imgSku"): sku,
        }

    def _get_ref_port_resource_names(self):
        # TODO
        pass

    def _get_network_interfaces(self):
        # TODO
        pass

    def _get_vm_properties(self):
        """ _get_vm_properties is a helper method which returns the dict of all
        auxiliary properties if the EC2 instance.
        """
        os_profile_data = self._get_base_os_profile_data()

        user_data = self._heat_resource.properties["UserData"]
        if user_data:
            os_profile_data["customData"] = (
                "[base64('%s')]" % json.dumps(user_data))

        vm_properties = self._get_base_vm_properties()
        vm_properties.update({
            "osProfile": os_profile_data,
            "networkProfile": {
                "networkInterfaces": self._get_network_interfaces(),
            }
        })
