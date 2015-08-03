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

from heat2arm import constants
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
    #   - get_dependencies.
    #   - get_resource_data.

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

        return base_vars

    def update_context(self):
        """ update_context adds all the necessary parameters, variables and
        resource data to the context required by this resource's translation.
        """
        super(EC2InstanceARMTranslator, self).update_context()

        res = self._context.get_resource({
            "type": self.heat_resource_type,
            "name": "[variables('vmName_%s')]" % self._heat_resource.name,
        })

        # check for the existence of an availability zone and add a
        # variable for its name, list it as a dependency and add it:
        avail_zone = self._get_availability_zone()
        if avail_zone:
            res["dependsOn"].append(
                "[concat('Microsoft.Compute/availabilitySets/',"
                "variables('availabilitySetName_%s'))]" % avail_zone
            )

            if avail_zone not in self._context.availability_set_names:
                self._context.add_variables({
                    "availabilitySetName_%s" % avail_zone:
                        "availabilitySet_%s" % avail_zone
                })

                self._context.add_resource({
                    "apiVersion": constants.ARM_API_VERSION,
                    "type": "Microsoft.Compute/availabilitySets",
                    "name": "[variables('availabilitySetName_%s')]" %
                            avail_zone,
                    "location": "[variables('location')]",
                    "properties": {}
                })

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
