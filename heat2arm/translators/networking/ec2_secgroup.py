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

from heat2arm.translators.networking.base_secgroup import (
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
                    "name": "secGroupRule_%d" % i,
                    "properties": {
                        "protocol": in_rule["IpProtocol"],
                        "sourcePortRange": in_rule["FromPort"],
                        "destionationPortRange": in_rule["ToPort"],
                        "sourceAddressPrefix": in_rule["CidrIp"],
                        "destinationAddressPrefix": "*",
                        "access": "Inbound",
                        # NOTE: priority is always fixed.
                        "priority": 100,
                    }
                }

                i = i + 1
                rules.append(rule)

        # traverse all ingress rules; if any:
        if "SecurityGroupEgress" in self._heat_resource.properties.data:
            for in_rule in self._heat_resource.properties.data[
                    "SecurityGroupEgress"]:
                # build the rule:
                rule = {
                    "name": "secGroupRule_%d" % i,
                    "properties": {
                        "protocol": in_rule["IpProtocol"],
                        "sourcePortRange": in_rule["FromPort"],
                        "destionationPortRange": in_rule["ToPort"],
                        "sourceAddressPrefix": in_rule["CidrIp"],
                        "destinationAddressPrefix": "*",
                        "access": "Outbound",
                        # NOTE: priority is always fixed.
                        "priority": 100,
                    }
                }

                i = i + 1
                rules.append(rule)

        return rules

    def get_variables(self):
        """ get_variables returns the dict of all the required ARM
        template variables for the EC2 security group.
        """
        return {
            self._make_var_name("secGroupName"): self._name,
        }

    def get_parameters(self):
        """ get_parameters returns the dict of ARM template parameters
        associated with the EC2 security group.

        It is no-op as there usually are no parameters for
        EC2 security groups.
        """
        return {}

    def get_dependencies(self):
        """ get_dependencies returns a list of resources which this resource
        depends on.

        It is no-op as Azure security groups are fully stand-alone resources.
        """
        return []

    def get_resource_data(self):
        """ get_resource_data returns a list of all the options associated to
        this resource which is directly serializable into JSON and used in the
        resulting ARM template for this resource.
        """
        resource_data = self._get_base_secgroup_header()
        resource_data.update({
            "properties": {
                "securityRules": self._get_rules()
            }
        })

        return [resource_data]
