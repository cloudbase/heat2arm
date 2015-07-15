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
    Contains the definition for the Neutron security group translator.
"""

from heat2arm.translators.networking.secgroups.base_secgroup import (
    BaseSecurityGroupARMTranslator
)


class NeutronSecurityGroupARMTranslator(BaseSecurityGroupARMTranslator):
    """ NeutronSecurityGroupARMTranslator is the translator
    for Neutron security groups.
    """
    heat_resource_type = "OS::Neutron::SecurityGroup"

    def _get_rules(self):
        """ _get_rules is a helper method which returns a list of all
        the resulting ARM security group rules to be created.
        """
        i = 0
        rules = []

        # traverse all the rules and add them:
        if "rules" in self._heat_resource.properties.data:
            for rule in self._heat_resource.properties.data["rules"]:
                # get the port range or default to *:
                port_range = "*"
                if "port_range_min" in rule and "port_range_max" in rule:
                    port_range = "%s-%s" % (
                        rule["port_range_min"],
                        rule["port_range_max"]
                    )

                direction = "Inbound"
                if "direction" in rule:
                    if direction == "egress":
                        direction = "Outbound"

                # build the new rule:
                new_rule = {
                    "name": "%s__rule_%d" % (self._name, i),
                    "properties": {
                        "protocol": rule["protocol"],
                        # NOTE:source and destination port ranges here coincide
                        # in conformity with Neutron's secgroup specification:
                        "sourcePortRange": port_range,
                        "destinationPortRange": port_range,
                        "sourceAddressPrefix": rule["remote_ip_prefix"],
                        # NOTE: defaulted to *:
                        "destinationAddressPrefix": "*",
                        "access": "Allow",
                        "direction": direction
                    }
                }

                i = i + 1
                rules.append(new_rule)

        return rules
