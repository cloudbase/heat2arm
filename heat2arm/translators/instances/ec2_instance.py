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

from heat2arm.translators.instances import ec2_utils as utils
from heat2arm.translators.instances.base_instance import (
    BaseInstanceARMTranslator
)


LOG = logging.getLogger(__name__)


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
            self._heat_resource.properties["ImageId"]
        )

        return {
            self._make_var_name("vmName"): self._name,
            self._make_var_name("vmSize"): utils.get_azure_flavor(
                self._heat_resource.properties["InstanceType"]
            ),
            self._make_var_name("imgPublisher"): publisher,
            self._make_var_name("imgOffer"): offer,
            self._make_var_name("imgSku"): sku,
        }

    # NOTE:the following methods are inherited from BaseInstanceARMTranslator:
    #   - get_parameters.
    #   - get_dependencies.
    #   - get_resource_data.

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_name is a helper method which returns a list
        of all the Neurton port resources wich reference this EC2 instance.
        """
        port_resource_names = []

        for resource in self._heat_resource.stack.iter_resources():
            # TODO: EC2 EIP Assocs here?
            if (resource.type() == "OS::Neutron::Port"
                    and "device_id" in resource.properties.data
                    and resource.properties.data["device_id"] == self._name):
                port_resource_names.append({
                    "id":
                        "[resourceId('Microsoft.Network/networkInterfaces'"
                        ", variables('nicName_%s'))]" % resource.name
                })

        return port_resource_names

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

        return vm_properties

    def _get_attached_volumes(self):
        """ Returns a list of all volumes attached to this instance.
        """
        lun = 0
        volumes = []

        for resource in self._heat_resource.stack.iter_resources():
            if (resource.type() == "AWS::EC2::VolumeAttachment" and
                    resource.properties.data["InstanceId"] == self._name):
                volume_name = resource.properties.data["VolumeId"].args
                volumes.append({
                    "name": self._name,
                    "diskSizeGB": "[parameters('size_%s')]" %
                                  volume_name,
                    "lun": lun,
                    "vhd": {
                        "Uri": "[variables(diskUri_%s)]" %
                               volume_name,
                    }
                })
                lun = lun + 1

        return volumes
