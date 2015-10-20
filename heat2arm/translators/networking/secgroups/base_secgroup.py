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
    Contains the base definition for both Neutron and EC2 security groups
    translations.
"""


from heat2arm.config import CONF
from heat2arm.translators.base import BaseHeatARMTranslator
from heat2arm.translators.networking.secgroups import exceptions


class BaseSecurityGroupARMTranslator(BaseHeatARMTranslator):
    """ BaseSecurityGroupARMTranslator is a specialised verions of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to be used in inheriting translators.
    """
    arm_resource_type = "Microsoft.Network/networkSecurityGroups"

    # _protocol_field_name stores the string representation of the
    # field which specifies the protocol a rule is managing:
    _protocol_field_name = ""

    # _mandatory_rule_fields is a list of the names of the fields that
    # all rules require:
    _mandatory_rule_fields = []

    def get_variables(self):
        """ get_variables returns the dict of all the required ARM
        template variables for the EC2 security group.
        """
        return {
            self._make_var_name("secGroupName"):
                self._make_var_name("secGroup"),
        }

    def get_resource_data(self):
        """ get_resource_data returns a list of all the options associated to
        this resource which is directly serializable into JSON and used in the
        resulting ARM template for this resource.
        """
        super(BaseSecurityGroupARMTranslator, self).get_resource_data()

        return [{
            "apiVersion": CONF.arm_api_version,
            "type": self.arm_resource_type,
            "name": ("[variables('secGroupName_%s')]" %
                     self._heat_resource.name),
            "location": "[variables('location')]",
            "properties": {
                "securityRules": self._get_rules()
            }
        }]

    def _get_rules(self):
        """ _get_rules is a helper method which returns a list of all
        the resulting ARM security group rules to be created
        following the translation.

        NOTE: it is stubbed and must be implemented in all inheriting classes.
        """
        return []

    def _validate_rules(self, rules):
        """ _validate_rules is a helper method which recieves a list of raw
        rule definitions and ensures that all the mandatory fields of the rule
        are specified and that the protocol specified within them is supported
        by Azure security groups.
        """
        supported_protos = ["tcp", "udp", "*"]  # NOTE: '*' = both udp and tcp

        for ruleno, rule in enumerate(rules):
            # first; check that the field is there in the first place:
            if self._protocol_field_name not in rule:
                raise exceptions.SecurityGroupMissingFieldException(
                    "'%s': security group '%s''s rule number %d has no '%s'"
                    "field defined." % (
                        self, self._heat_resource_name,
                        ruleno + 1, self._protocol_field_name
                    )
                )

            # then, ensure the protocol is ok:
            proto = rule[self._protocol_field_name]
            if proto.lower() not in supported_protos:
                raise exceptions.SecurityGroupInvalidFieldException(
                    "'%s': security group '%s' rule number %d has an invalid '"
                    "%s' field: '%s'. Valid protocols are 'tcp', 'udp' and '*'"
                    % (
                        self, self._heat_resource_name, ruleno + 1,
                        self._protocol_field_name, proto
                    )
                )

            # lastly, check for all the other mandatory fields:
            for field in self._mandatory_rule_fields:
                if field not in rule:
                    raise exceptions.SecurityGroupMissingFieldException(
                        "'%s': security group '%s' rule number %d's '%s' field"
                        " is missing." % (
                            self, self._heat_resource_name, ruleno + 1, field
                        )
                    )
