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

from heat2arm.constants import ARM_API_VERSION
from heat2arm.translators import global_constants
from heat2arm.translators.instances import ec2_utils as utils
from heat2arm.translators.instances.base_instance import (
    BaseInstanceARMTranslator
)


class EC2InstanceARMTranslator(BaseInstanceARMTranslator):
    """ EC2InstanceARMTranslator is the translator associated to an EC2
    instance.

        It does a couple of things specific to CFN, and namely:
    - it also defines availabilitySets for each AvailabilityZone
    of each instance.
    """
    heat_resource_type = "AWS::EC2::Instance"

    # NOTE:the following methods are inherited from BaseInstanceARMTranslator:
    #   - get_parameters.

    def get_variables(self):
        """ get_variables returns a dict of ARM template variables
        associated with the Heat template's resource translation.
        """
        base_vars = self._get_base_variables()

        (publisher, offer, sku) = utils.get_azure_image_info(
            self._heat_resource.properties["ImageId"]
        )

        base_vars.update({
            self._make_var_name("vmSize"): utils.get_azure_flavor(
                self._heat_resource.properties["InstanceType"]
            ),
            self._make_var_name("imgPublisher"): publisher,
            self._make_var_name("imgOffer"): offer,
            self._make_var_name("imgSku"): sku,
        })

        # check for the existence of an availability zone and add a
        # variable with its name if required:
        avail_zone = self._get_availability_zone()
        if avail_zone and (avail_zone not in
                           global_constants.AVAILABILITY_SET_NAMES):
            base_vars.update({
                "availabilitySetName_%s" % avail_zone:
                    "availabilitySet_%s" % avail_zone
            })

        return base_vars

    def get_dependencies(self):
        """ get_dependencies returns a list of all the dependencies
        of the EC2 instance's translation.
        """
        base_deps = super(EC2InstanceARMTranslator, self).get_dependencies()

        # check if the instance is in an availability zone and
        # thus requires a resulting availability set:
        avail_zone = self._get_availability_zone()
        if avail_zone:
            base_deps.append(
                "[concat('Microsoft.Compute/availabilitySets/',"
                "variables('availabilitySetName_%s'))]" % avail_zone
            )

        return base_deps

    def get_resource_data(self):
        """ get_resource_data returns a list of the resource data this resource
        will be translated to.
        """
        base_res_data = super(EC2InstanceARMTranslator,
                              self).get_resource_data()

        # check for the availability zone, and add it now, if required:
        avail_zone = self._get_availability_zone()
        if avail_zone and (avail_zone not in
                           global_constants.AVAILABILITY_SET_NAMES):
            base_res_data.append({
                "apiVersion": ARM_API_VERSION,
                "type": "Microsoft.Compute/availabilitySets",
                "name": "[variables('availabilitySetName_%s')]" % avail_zone,
                "location": "[variables('location')]",
                "properties": {}
            })
            global_constants.AVAILABILITY_SET_NAMES.append(avail_zone)

        return base_res_data

    def _get_vm_properties(self):
        """ _get_vm_properties is a helper method which returns all the
        properties of the instance's ARM translation.
        """
        base_props = super(EC2InstanceARMTranslator,
                           self)._get_vm_properties()

        avail_zone = self._get_availability_zone()
        if avail_zone:
            base_props.update({
                "availabilitySet": {
                    "id": "[resourceId('Microsoft.Compute/availabilitySets',"
                          "variables('availabilitySetName_%s'))]" % avail_zone
                }
            })

        return base_props

    def _get_ref_port_resource_names(self):
        """ _get_ref_port_resource_name is a helper method which returns a list
        of all the Neurton port resources wich reference this EC2 instance.
        """
        port_resource_names = []

        for resource in self._heat_resource.stack.iter_resources():
            # NOTE: because you can define both Neutron networking resources
            # and AWS ones in heat templates; we must check for both here:
            if (resource.type() == "OS::Neutron::Port"
                    and "device_id" in resource.properties.data
                    and resource.properties.data["device_id"] == self._name):
                port_resource_names.append(resource.name)
            if (resource.type() == "AWS::EC2::EIPAssociation"
                    and "InstanceId" in resource.properties.data
                    and resource.properties.data["InstanceId"] == self._name):
                port_resource_names.append(resource.name)

        return port_resource_names

    def _get_availability_zone(self):
        """ _get_availability_zone is a helper method which returns the
        AvailabilityZone this instance is located in, if any.
        """
        if "AvailabilityZone" in self._heat_resource.properties:
            return self._heat_resource.properties["AvailabilityZone"]

    def _get_userdata(self):
        """ _get_userdata is a helper method which returns the userdata
        from the instance's definition, if any.
        """
        if 'UserData' in self._heat_resource.properties:
            return self._heat_resource.properties['UserData']

        return ""

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
                    "name": volume_name,
                    "diskSizeGB": "[parameters('size_%s')]" %
                                  volume_name,
                    "lun": lun,
                    "vhd": {
                        "Uri": "[variables('diskUri_%s')]" %
                               volume_name,
                    },
                    "createOption": "Empty"
                })
                lun = lun + 1

        return volumes
