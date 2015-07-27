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
    Contains the definition for the EC2 security group translator.
"""

from heat2arm.translators.networking.secgroups.base_secgroup import (
    BaseSecurityGroupARMTranslator
)


class EC2SecurityGroupARMTranslator(BaseSecurityGroupARMTranslator):
    """ EC2SecurityGroupARMTranslator is the translator
    for EC2 security groups.
    """
    heat_resource_type = "AWS::EC2::SecurityGroup"

    def _get_rules(self):
        """ _get_rules is a helper method which returns a list of all
        the resulting ARM security group rules to be created.
        """
        i = 0
        rules = []

        # traverse all ingress rules; if any:
        if "SecurityGroupIngress" in self._heat_resource.properties.data:
            for in_rule in self._heat_resource.properties.data[
                    "SecurityGroupIngress"]:
                # build the rule:
                rule = {
                    "name": "%s_rule_%d" % (self._name, i),
                    "properties": {
                        "protocol": in_rule["IpProtocol"],
                        "sourcePortRange": in_rule["FromPort"],
                        "destinationPortRange": in_rule["ToPort"],
                        "sourceAddressPrefix": in_rule["CidrIp"],
                        "destinationAddressPrefix": "*",
                        "direction": "Inbound",
                        "access": "Allow",
                        # NOTE: priority is always fixed.
                        "priority": 100 + i,
                    }
                }

                i = i + 1
                rules.append(rule)

        # traverse all egress rules; if any:
        if "SecurityGroupEgress" in self._heat_resource.properties.data:
            for out_rule in self._heat_resource.properties.data[
                    "SecurityGroupEgress"]:
                # build the rule:
                rule = {
                    "name": "%s_rule_%d" % (self._name, i),
                    "properties": {
                        "protocol": out_rule["IpProtocol"],
                        "sourcePortRange": out_rule["FromPort"],
                        "destinationPortRange": out_rule["ToPort"],
                        "sourceAddressPrefix": out_rule["CidrIp"],
                        "destinationAddressPrefix": "*",
                        "direction": "Outbound",
                        "access": "Allow",
                        # NOTE: priority is always fixed.
                        "priority": 100 + i,
                    }
                }

                i = i + 1
                rules.append(rule)

        return rules
