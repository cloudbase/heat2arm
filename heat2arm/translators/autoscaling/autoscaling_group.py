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
    Contains the definition for the AWS AutoScalingGroup translator.
"""

import logging

from heat2arm.config import CONF
from heat2arm.translators.base import BaseHeatARMTranslator
from heat2arm.translators.autoscaling import exceptions
from heat2arm.translators.autoscaling import utils as autoscale_utils
from heat2arm.translators.autoscaling import constants as autoscale_constants


LOG = logging.getLogger("__heat2arm__")


class AWSAutoScalingGroupARMTranslator(BaseHeatARMTranslator):
    """ AWSAutoScalingGroupARMTranslator is the translator for an
    AutoScalingGroup from CFN.

    It maps relatively cleanly into a set of Azure autoscaleSettings which is
    applied to an availabilitySet (the mapping of an AWS AvailabilityZone).
    However, some other components of the autoscaleSettings resource must be
    derived from a handful of different other AWS resources.
    """
    heat_resource_type = "AWS::AutoScaling::AutoScalingGroup"
    arm_resource_type = "Microsoft.Insights/autoscaleSettings"

    def __init__(self, heat_resource, context):
        """ In addition to the base translator; AutoScalingGroup translators
        also posses a couple of flags which help coordinate the translation
        process.
        """
        super(AWSAutoScalingGroupARMTranslator, self).__init__(
            heat_resource, context
        )

        # _requires_own_avail_set marks whether or not a new availabilitySet
        # should be defined to support this AutoScalingGroup's translation:
        self._requires_own_avail_set = False

        # _required_avail_set_name holds the identifier of the availabilitySet
        # to be defined later in update_context if it's required:
        self._required_avail_set_name = ""

    def get_variables(self):
        """ get_variables returns the dict of all variables associated
        with the ARM definition of the resource.
        """
        variables = {
            "autoscaleSettingsName_%s" % self._heat_resource_name:
                "autoscaleSettings_%s" % self._heat_resource_name,
        }

        return variables

    def get_resource_data(self):
        """ get_resource_data returns the dict of data associated with the
        definition of the resource in Azure.
        """
        # NOTE: this must be done first in order to consistently
        # pre-obtain the target.
        target = self._get_target()

        return [{
            "name": "[variables('autoscaleSettingsName_%s')]" % (
                self._heat_resource_name
            ),
            # NOTE: autoscaleSettings specifically require this API version:
            "apiVersion": CONF.arm_autoscale_settings_api_version,
            "type": self.arm_resource_type,
            "location": "[variables('location')]",
            # "tags": {},    # NOTE
            "dependsOn": [
                "[concat('Microsoft.Compute/availabilitySets/', "
                "variables('availabilitySetName_%s'))]" % (
                    self._required_avail_set_name
                )
            ],
            "properties": {
                "targetResourceUri": target,
                "enabled": False,
                "profiles": [self._get_profile()],
            },
        }]

    def update_context(self):
        """ update_context adds all the necessary parameters, variables and
        resource data to the context required by this resource's translation.
        """

        # add an availabilitySet especially for the instance which is the
        # target of this AutoScalingGroup, if required:
        if self._requires_own_avail_set:
            # first; check whether the availability set already exists:
            if (self._required_avail_set_name in
                    self._context.availability_set_names):
                # if so; return gracefully here:
                return
            else:
                # first; add the availabilitySet variables and resource,
                # and register it to the list of availability sets:
                self._context.add_variables({
                    "availabilitySetName_%s" % self._required_avail_set_name:
                        "availabilitySet_%s" % self._required_avail_set_name
                })
                self._context.add_resource({
                    "apiVersion": CONF.arm_api_version,
                    "type": "Microsoft.Compute/availabilitySets",
                    "name": "[variables('availabilitySetName_%s')]" % (
                        self._required_avail_set_name
                    ),
                    "location": "[variables('location')]",
                    "properties": {
                        "platformFaultDomainCount": "2"
                    }
                })
                self._context.availability_set_names.append(
                    self._required_avail_set_name
                )

                # then; also add it as a dependency and reference to the
                # target instance itself:
                instance = self._context.get_arm_resource({
                    "type": "Microsoft.Compute/virtualMachines",
                    "name": "[variables('vmName_%s')]" % (
                        self._required_avail_set_name
                    )
                })
                instance["dependsOn"].append(
                    "[concat('Microsoft.Compute/availabilitySets/', "
                    "variables('availabilitySetName_%s'))]" % (
                        self._required_avail_set_name
                    )
                )

                instance["properties"]["availabilitySet"] = {
                    "id":
                        "[resourceId('Microsoft.Compute/availabilitySets', "
                        "variables('availabilitySetName_%s'))]" % (
                            self._required_avail_set_name
                        )
                }

    def _get_target(self):
        """ _get_target returns the URI of the resource the autoscalingSettings
        should be applied to. The target is always an autoscalingSet which is
        injected into either the Instance or the LaunchConfiguration the
        AutoScalingGroup targets.
        """
        # first; check if the banal "InstanceId" is set:
        if "IntanceId" in self._heat_resource.properties:
            return self._get_instance_avail_set(
                self._heat_resource.properties["InstanceId"]
            )

        # else; check for the "LaunchConfigurationName" field and try and
        # deduce the availabilitySet of the Instances the LaunchConfig is
        # applied to:
        if "LaunchConfigurationName" in self._heat_resource.properties:
            return self._get_launch_config_avail_set(
                self._heat_resource.properties["LaunchConfigurationName"]
            )

        # lastly; check if the "AvailabilityZones" field is set:
        if "AvailabilityZones" in self._heat_resource.properties:
            avail_zones = self._heat_resource.properties["AvailabilityZones"]
            if not len(avail_zones) > 0:
                raise exceptions.AutoScalingGroupInvalidFieldException(
                    "'%s': 'AvailabilityZones' field for '%s' must have "
                    "at least one value." % (
                        self,
                        self._heat_resource_name
                    )
                )

            # if the AutoScalingGroup happens to have more than one
            # AvailabilityZone; log the possible discrepancy:
            if len(avail_zones) > 1:
                LOG.warn(
                    "'%s': AutoScalingGroup '%s' has more than one "
                    "AvailabilityZone set. Defaulting to the first one: '%s'.",
                    self,
                    self._heat_resource_name,
                    avail_zones[0]
                )

            return ("[resourceId('Microsoft.Compute/availabilitySets', "
                    "variables('availabilitySetName_%s'))]" % avail_zones[0])

    def _get_launch_config_avail_set(self, launch_config_name):
        """ _get_launch_config_avail_set is a helper method which recieves the
        name of a LaunchConfiguration and returns the fully qualified URI of
        the resulting Azure availabilitySet which the instances partaking in
        the LaunchConfiguration will be a part of.
        """
        # first; make sure the LaunchConfiguration is defined:
        if launch_config_name not in self._context.heat_resource_stack:
            raise exceptions.AutoScalingGroupInvalidFieldException(
                "'%s': referenced LaunchConfiguration '%s' doesn't exist." % (
                    self, launch_config_name
                )
            )

        #  default to returning the uri of an availabilitySet we will be
        # creating especially for this AutoScalingGroup's instance.
        # NOTE: considering LaunchConfigs are translated roughly the same way
        # as instances; we simply apply the same logic here:
        self._requires_own_avail_set = True
        self._required_avail_set_name = launch_config_name
        return autoscale_utils.create_avail_set_uri(launch_config_name)

    def _get_instance_avail_set(self, instance_name):
        """ _get_instance_avail_set is a helper method which, given the
        name of an instance, returns the fully qualified URI of the
        availabilitySet the instance is a part of.
        """
        # first; check for the instance's existence:
        if instance_name not in self._context.heat_resource_stack:
            raise exceptions.AutoScalingGroupInvalidFieldException(
                "'%s': referenced Instance '%s' does not exist." % (
                    self, instance_name
                )
            )

        instance = self._context.heat_resource_stack[instance_name]
        # now; check if the instance has an explicit AvailabilityZone set:
        if 'AvailabilityZone' in instance.properties:
            # if so, return a reference to the availabilitySet
            # which the EC2InstanceTranslator will create:
            self._required_avail_set_name = instance_name
            return autoscale_utils.create_avail_set_uri(
                instance.properties["AvailabilityZone"]
            )

        # else, default to returning the uri of an availabilitySet we will be
        # creating especially for this AutoScalingGroup's instance.
        # NOTE: we must also set _requires_own_avail_set beforehand:
        self._requires_own_avail_set = True
        self._required_avail_set_name = instance_name
        return autoscale_utils.create_avail_set_uri(instance_name)

    def _get_profile(self):
        """ _get_profile returns the single profile for the autoscaleSettings.
        """
        return {
            "name": "autoscaleSettingsProfile_%s" % self._heat_resource_name,
            "capacity": self._get_capacity(),
            "rules": self._get_rules(),
        }

    def _get_capacity(self):
        """ _get_capacity is a helper method which returns the dictionary of
        capacity values for the profile for the new Azure autoscaleSettings.
        """
        maximum = int(self._heat_resource.properties["MaxSize"])
        minimum = int(self._heat_resource.properties["MinSize"])
        if not minimum > 0:
            # unlikely, but must be sure:
            raise exceptions.AutoScalingGroupInvalidFieldException(
                "'MinSize' of AWS AutoScalingGroup '%s' is 0!" % (
                    self._heat_resource_name
                )
            )

        # NOTE: default is the mean of the min and max by default:
        default = int((minimum + maximum) / 2)  # Python 3 futureproof'd
        if "DesiredCapacity" in self._heat_resource.properties:
            default = self._heat_resource.properties["DesiredCapacity"]

        return {
            "minimum": str(minimum),
            "default": str(default),
            "maximum": str(maximum)
        }

    def _get_rules(self):
        """ _get_rules is a helper method which returns the rules to be applied
        for the scaling of all the instances the autoscaleSettings encompass.
        """
        scaling_policies = []

        # first; we must search for any ScalingPolicies which are
        # applied for this AutoScalingGroup:
        for resource in self._context.heat_resources:
            if resource.type == "AWS::AutoScaling::ScalingPolicy":
                # check for the AutoScalingGroupName field:
                if "AutoScalingGroupName" not in resource.properties:
                    # the 'AutoScalingGroupName' field is mandatory:
                    raise exceptions.AutoScalingGroupMissingFieldException(
                        "'%s': ScalingPolicy '%s' mandatory "
                        "'AutoScalingGroupName' field missing." % (
                            self, resource.name
                        )
                    )
                # check if the ScalingPolicy applies to this AutoScalingGroup:
                if (resource.properties[
                        "AutoScalingGroupName"] == self._heat_resource_name):
                    scaling_policies.append(resource)

        # now check if any ScalingPolicies were specified in the first place:
        if not scaling_policies:
            # then, simply log a warning stating we are falling
            # back to defaults:
            LOG.warning(
                "'%s': AutoScalingGroup '%s' has no associated ScalingPolicies"
                " which can be translated into autoscaleSettings rules. "
                "Falling back to using 'default_autoscaling_rules'.",
                self, self._heat_resource_name
            )

            rules = CONF.default_autoscaleSettings_rules
            # add the appropriate target to the defaults and retun them:
            for rule in rules:
                rule["metricTrigger"]["metricResourceUri"] = self._get_target()
            return rules

        # else; return all the translations for the given policies:
        return [self._translate_scaling_policy(p) for p in scaling_policies]

    def _translate_scaling_policy(self, scaling_policy):
        """ _translate_scaling_policy is a helper method which takes a given
        AWS::AutoScaling::ScalingPolicy and returns the equivalent rule for
        a resulting Azure autoscaleSettings.
        """
        # rule is the template of the rule which will be created.
        # it contains a bunch of sensible defaults:
        rule = {
            "metricTrigger": {
                "metricName": "CpuPercentage",
                "metricResourceUri": self._get_target(),
                "timeGrain": "PT1M",
                "statistic": "Average",
                "timeWindow": "PT10M",
                "timeAggregation": "Average",
            },
            "scaleAction": {
                "cooldown": "PT10M"
            }
        }

        # check for the mandatory "AdjustmentType" field:
        if "AdjustmentType" not in scaling_policy.properties:
            raise exceptions.AutoScalingGroupMissingFieldException(
                "'%s': ScalingPolicy '%s' has no 'AdjustmentType' field." % (
                    self, scaling_policy.name
                )
            )

        # then, go ahead with the actual translation:
        rule["scaleAction"][
            "type"
        ] = autoscale_constants.ADJUSTMENT_TYPE_TO_SCALE_TYPE_MAP[
            scaling_policy.properties["AdjustmentType"]
        ]

        # check for the cooldown period:
        if "Cooldown" in scaling_policy.properties:
            rule["scaleAction"][
                "cooldown"
            ] = autoscale_utils.seconds_to_iso_minutes(
                scaling_policy.properties["Cooldown"]
            )

        # check for the actual value of the policy:
        if "ScalingAdjustment" not in scaling_policy.properties:
            raise exceptions.AutoScalingGroupMissingFieldException(
                "'%s': ScalingPolicy '%s' for AutoScalingGroup '%s' has "
                "no 'ScalingAdjustment' field set." % (
                    self, scaling_policy.name, self._heat_resource_name
                )
            )
        scale_value = int(scaling_policy.properties["ScalingAdjustment"])

        # now; update all the required parameters with regards to the
        # scaling adjustment value:
        if scale_value > 0:
            rule["metricTrigger"].update({
                "operator": "GreaterThan",
                "threshold": CONF.autoscaling_max_cpu_threshold
            })
            rule["scaleAction"].update({
                "direction": "Increase",
                "value": "%s" % (scale_value)
            })
        else:
            rule["metricTrigger"].update({
                "operator": "LessThan",
                "threshold": CONF.autoscaling_min_cpu_threshold
            })
            rule["scaleAction"].update({
                "direction": "Decrease",
                "value": "%s" % (-scale_value)
            })

        return rule
