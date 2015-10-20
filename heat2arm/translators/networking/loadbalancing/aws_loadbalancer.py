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
    This module defines the translator for AWS's LoadBalancer.
"""

import logging

from heat2arm.translators.networking.loadbalancing import exceptions
from heat2arm.translators.networking.loadbalancing.base import (
    BaseLoadBalancerARMTranslator
)


LOG = logging.getLogger("__heat2arm__")


class AWSLoadBalancerARMTranslator(BaseLoadBalancerARMTranslator):
    """ AWSLoadBalancerARMTranslator is the translator for AWS LoadBalancers.
    """

    heat_resource_type = "AWS::ElasticLoadBalancing::LoadBalancer"

    _mandatory_rule_fields = ['LoadBalancerPort', 'InstancePort', 'Protocol']

    def _get_nat_rules(self):
        """ _get_nat_rules is a helper method which returns the dict of
        NAT rule names mapped to their actual data.

        It goes ahead and translates all of the ElasticLoadBalancingListeners
        into their respective Azure inbountNatRule.
        """
        # first; check that the 'Listeners' field exists:
        if 'Listeners' not in self._heat_resource.properties:
            raise exceptions.LoadBalancerMissingFieldException(
                "'%s': LoadBalancer '%s' has no 'Listeners' field set." % (
                    self, self._heat_resource_name
                )
            )

        # then translate each Listener into its corresponding NatRule:
        rules = []
        for i, listener in enumerate(
                self._heat_resource.properties['Listeners']):
            # first; validate the listener:
            self._check_rule(listener)

            # then, check the specified protocol:
            proto = listener["Protocol"].lower()
            if proto not in ["http", "https", "udp", "tcp", "ssl"]:
                raise exceptions.LoadBalancerInvalidFieldException(
                    "'%s': LoadBalancer '%s' rule number %d has an invalid"
                    "protocol specified: '%s'.", self,
                    self._heat_resource_name, proto
                )

            # now, check that the protocol isn't the trivial TCP or UDP
            # and if so, log that we are defaulting to TCP:
            if proto not in ["udp", "tcp"]:
                self._logger.warning(
                    "Protocol '%s' not supported on Azure, defaulting"
                    "to using 'tcp'.", proto
                )

                proto = "tcp"


            rules.append({
                "name": "%s_rule_%d" % (self._heat_resource_name, i),
                "properties": {
                    "protocol": proto,
                    "frontendPort": listener["LoadBalancerPort"],
                    "backendPort": listener["InstancePort"],
                    "enableFloatingIP": False,
                    "frontendIPConfiguration": {
                        "id": "[variables('frontendIPConfigID_%s')]" %
                              self._heat_resource_name
                    }
                }
            })

        return rules

    def _get_nic_for_instance(self, instance_name):
        """ _get_nic_for_instance is a helper method which returns the name of
        the nic for the given instance.
        """
        if instance_name not in self._context.heat_resource_stack:
            raise exceptions.LoadBalancerInvalidFieldException(
                "'%s': referenced instance '%s' is not defined." % (
                    self, instance_name
                )
            )

        # now, go ahead and get the nics:
        nics = []
        for resource in self._context.heat_resources:
            if (resource.type == "AWS::EC2::EIPAssociation"
                    and "InstanceId" in resource.properties
                    and resource.properties["InstanceId"] ==
                    instance_name):
                nics.append(resource.name)

        if not nics:
            # it means that there are no nic-like resources defined on the
            # instance itself, so thus a default one will be created and we
            # will reference that:
            return "[variables('nicName_VM_%s')]" % instance_name
        elif len(nics) == 1:
            return "[variables('nicName_%s')]" % nics[0]

        # else, due to the fact that we cannot accurately deduce which is the
        # network interface we must apply the load balancing behind, we log a
        # warning and just take the first one:
        self._logger.warning(
            "load balancer target instance '%s' has multiple nics traffic"
            "can be balanced on. Defaulting to using '%s'.",
            instance_name, nics[0]
        )
        return "[variables('nicName_%s')]" % nics[0]

    def _get_nic(self):
        """ _get_nic is a helper method which returns the name of the
        nic which the loadbalancing will happen on.

        Unfortunately, there is no easier way of obtaining it than:
            - look for the 'Instances' field and getting their nics
            - else, look for a referencing AutoScalingGroup, see which
              Instances/LaunchConfigs they reference and get their nics

        get nic name through VM/Launchconfig from referencing ASG
        """
        # first; check for the 'Instances' field:
        if 'Instances' in self._heat_resource.properties:
            instances = self._heat_resource.properties["Instances"]

            if len(instances) > 1:
                self._logger.warning(
                    "LoadBalancer '%s' has more than one instance given "
                    "under 'Instances'. Only translating for the first one: "
                    "'%s'.", self._heat_resource_name, instances[0]
                )

            return self._get_nic_for_instance(instances[0])

        # else, look for an AutoScalingGroup which references
        # this LoadBalancer under 'LoadBalancers':
        for resource in self._context.heat_resources:
            if (resource.type == "AWS::AutoScaling::AutoScalingGroup"
                    and 'LoadBalancerNames' in resource.properties
                    and self._heat_resource_name in resource.properties[
                        'LoadBalancerNames'
                    ]):
                # if found; retrieve the instance/LaunchConfig for the ASG:
                if 'InstanceId' in resource.properties:
                    return self._get_nic_for_instance(
                        resource.properties["InstanceId"]
                    )

                if 'LaunchConfigurationName' in resource.properties:
                    return self._get_nic_for_instance(
                        resource.properties["LaunchConfigurationName"]
                    )

                # else, raise an exception here:
                raise exceptions.LoadBalancerInvalidFieldException(
                    "'%s': referencing AutoScalingGroup '%s' has neither an "
                    "'InstanceId' or 'LaunchConfigurationName' field set." %
                    (self, resource.name)
                )

        raise exceptions.LoadBalancerMissingFieldException(
            "'%s': cannot determine target NIC for LoadBalancer '%s'." %
            (self, self._heat_resource_name)
        )
