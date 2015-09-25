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
    This module contains the definition of the AWS LaunchConfig translator.
"""

import copy

from heat2arm.translators.autoscaling import exceptions
from heat2arm.translators.instances.ec2_instance import (
    EC2InstanceARMTranslator
)


class AWSLaunchConfigurationARMTranslator(EC2InstanceARMTranslator):
    """ AWSLaunchConfigurationARMTranslator is the translator for LaunchConfigs.

    Considering LaunchConfigs are practically nothing more than templates for
    instances; we inherit directly from the EC2 Instance translator with minor
    changes.
    """
    heat_resource_type = "AWS::AutoScaling::LaunchConfiguration"

    def __init__(self, heat_resource, context):
        """ Considering that AWS LaunchConfigurations may have an 'InstanceId'
        field specified which will act as a 'base' for all the settings of the
        LaunchConfiguration; we must do some patchwork magic before passing the
        resource data to the EC2InstanceARMTranslator.
        """
        # _backing_instance holds the Instance who's properties this
        # LaunchConfiguration's are based (if applicable):
        self._backing_instance = None

        # first; check for the 'InstanceId' field of the LaunchConfiguration:
        if 'InstanceId' in heat_resource.properties:
            # we must first fetch the resource data of the Instance:
            instance_name = heat_resource.properties["InstanceId"]
            if instance_name not in context.heat_resource_stack:
                raise exceptions.LaunchConfigurationInvalidFieldException(
                    "'%s': referenced Instance '%s' for LaunchConfiguration"
                    "'%s' is not defined." % (
                        self, instance_name, heat_resource.name
                    )
                )
            self._backing_instance = context.heat_resource_stack[instance_name]

            # TODO(aznashwan): account for BlockStorageProfile not being
            # overriden after it gets implemented in EC2InstanceARMTranslator.

            # then, we must copy the Instance's properties and apply the diffs
            # of the LaunchConfig's properties:
            instance_props = copy.deepcopy(self._backing_instance.properties)
            instance_props.update(heat_resource.properties)
            heat_resource.properties = instance_props

        # lastly; go ahead and run the EC2InstanceARMTranslator's init:
        super(AWSLaunchConfigurationARMTranslator, self).__init__(
            heat_resource, context
        )
