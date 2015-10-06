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
    This module contains the definitions for the translators of the two AWS
    SecurityGroup rules which are definable outside security groups themselves
"""

import logging

from heat2arm.translators.base import BaseHeatARMTranslator
from heat2arm.translators.networking.secgroups import exceptions


LOG = logging.getLogger("__heat2arm__")


class BaseEC2SecurityGroupRuleARMTranslator(BaseHeatARMTranslator):
    """ BaseEC2SecurityGroupRuleARMTranslator is the base class of all EC2
    SecurityGroup rule translators.

    All inheriting translators will rely wholly on update_context to "inject"
    themselves into an already defined SecurityGroup.
    """

    # NOTE: stand-alone security group rules get 'injected' into security
    # groups themselves, so they will not have a resulting translation:
    arm_resource_type = ""

    # _rule_direction denotes the direction of traffic the translated
    # security rule group is meant to regulate:
    _rule_direction = ""

    # _target_secgroup_field_name is the name of the field containing a
    # reference to the SecurityGroup which this rule resource is targetting.
    _target_secgroup_field_name = ""

    def get_variables(self):
        """ get_variables returns the dict of all the required ARM
        template variables for the EC2 security group.

        It is no-op as no variables must be defined for translation.
        """
        return {}

    def get_parameters(self):
        """ get_parameters returns the dict of ARM template parameters
        associated with the EC2 security group.

        It is no-op as there usually are no parameters for
        EC2 security group rules.
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
        return []

    def update_context(self):
        """ update_context 'injects' the rule obtained from _get_rule into the
        data of the security group obtained from _get_target.
        """
        secgroup = self._context.get_arm_resource({
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "[variables('secGroupName_%s')]" % self._get_target(),
        })

        rule = self._get_rule()
        # first; add the priority field based on how many rules
        # the security group already has defined:
        rule["properties"]["priority"] = len(
            secgroup["properties"]["securityRules"]
        ) + 100

        # then, append the rule to the security group:
        secgroup["properties"]["securityRules"].append(rule)

    def _validate_input_rule(self):
        """ _validate_input_rule is a helper method which checks the provided
        SecurityGroupRule resource's fields for all the mandatory ones.
        """
        mandatories = ["IpProtocol", "FromPort", "ToPort"]

        for field in mandatories:
            if field not in self._heat_resource.properties:
                raise exceptions.SecurityGroupMissingFieldException(
                    "'%s': security group rule resource '%s' has no '%s' "
                    "field." % (self, self._heat_resource_name, field)
                )

        # validate the value of IpProtocol:
        allowed_protos = ["tcp", "udp", "*"]
        if (self._heat_resource.properties["IpProtocol"].lower() not in
                allowed_protos):
            raise exceptions.SecurityGroupInvalidFieldException(
                "'%s': Invalid value '%s' provided for 'IpProtocol'. "
                "only include 'tcp', 'udp' and '*'.", self,
                self._heat_resource.properties["IpProtocol"]
            )

    def _get_rule(self):
        """ _get_rule returns the resulting ARM rule to be injected into
        the target security group.
        """
        self._validate_input_rule()

        return {
            "name": "%s_rule" % (self._heat_resource_name),
            "properties": {
                "protocol": self._heat_resource.properties["IpProtocol"],
                "sourcePortRange": self._heat_resource.properties["FromPort"],
                "destinationPortRange":
                    self._heat_resource.properties["ToPort"],
                "sourceAddressPrefix": self._get_cidr(),
                "destinationAddressPrefix": "*",
                "direction": self._rule_direction,
                "access": "Allow",
            }
        }

    def _get_cidr(self):
        """ _get_cidr is a helper method which returns the cidr
        representing the object of the SecurityGroupRule.

        This process is not as simple as simply looking for a 'CidrIp' field
        in the data of the rule, as it is optional and may be missing.
        """
        # first; check for the banal 'CidrIp' field:
        if "CidrIp" in self._heat_resource.properties:
            # if found; simply return it:
            return self._heat_resource.properties["CidrIp"]

        # else, we must try and fetch the 'CidrIp' from the target
        # security group's rules themselves:

        # first; check for the field:
        if (self._target_secgroup_field_name not in
                self._heat_resource.properties):
            raise exceptions.SecurityGroupMissingFieldException(
                "'%s': both the 'CidrIp' and '%s' fields are missing from "
                "security group rule '%s'." % (
                    self, self._target_secgroup_field_name,
                    self._heat_resource_name
                )
            )

        # now, check that the referenced security group actually exists:
        target_group_name = self._heat_resource.properties[
            self._target_secgroup_field_name
        ]
        if target_group_name not in self._context.heat_resource_stack:
            raise exceptions.SecurityGroupNotFoundException(
                "'%s': referenced security group '%s' does not exist." % (
                    self, target_group_name
                )
            )

        # if here; log a warning saying inference was attempted:
        LOG.warning(
            "'%s': 'CidrIp' not set on '%s'. Attempting to infer it from "
            "the target SecurityGroup '%s'.",
            self, self._heat_resource_name, target_group_name
        )

        # then, fetch the target group and collect all of their Cidr fields:
        cidrs = []
        target_group = self._context.heat_resource_stack[target_group_name]
        if "SecurityGroupIngress" in target_group.properties:
            for rule in target_group.properties["SecurityGroupIngress"]:
                if "CidrIp" in rule:
                    cidrs.append(rule["CidrIp"])
        if "SecurityGroupEgress" in target_group.properties:
            for rule in target_group.properties["SecurityGroupEgress"]:
                if "CidrIp" in rule:
                    cidrs.append(rule["CidrIp"])

        # reduce to check if there is a single definitive Cidr to be used:
        cidrs = set(cidrs)
        if not len(cidrs) == 1:
            raise exceptions.SecurityGroupInvalidFieldException(
                "'%s': Unable to infer target Cidr of SecurityGroup '%s' for "
                "the security group rule '%s'." % (
                    self, target_group_name, self._heat_resource_name
                )
            )

        # else, log and return the single possible cidr deduced:
        LOG.warning(
            "'%s': succesfully deduced that security group rule '%s' cidr is "
            " most likely '%s' based on the SecurityGroup it targets.",
            self, self._heat_resource_name, list(cidrs)[0]
        )
        return list(cidrs)[0]

    def _get_target(self):
        """ _get_target is a helper method which retuns the name of the target
        SecurityGroup the rule should e applied to.

        It is stubbed and should be implemented by all inheriting classes.
        """
        pass


class EC2SecurityGroupRuleIngressARMTranslator(
        BaseEC2SecurityGroupRuleARMTranslator):
    """ EC2SecurityGroupRuleIngressARMTranslator is the translator for CFN
    AWS::EC2::SecurityGroupIngress resources.

    It 'injects' the translated rule into the resulting ARM security group.
    """

    heat_resource_type = "AWS::EC2::SecurityGroupIngress"

    _rule_direction = "Inbound"

    _target_secgroup_field_name = "SourceSecurityGroupName"

    def _get_target(self):
        """ _get_target returns the target SecurityGroup of the rule.

        SecurityGroupIngress rules can specify the target group through either
        a 'GroupId' or 'GroupName' field.
        """
        target_group = ""

        if 'GroupName' in self._heat_resource.properties:
            target_group = self._heat_resource.properties["GroupName"]
        elif 'GroupId' in self._heat_resource.properties:
            target_group = self._heat_resource.properties["GroupId"]

        # check that the target does indeed exist:
        if not target_group:
            raise exceptions.SecurityGroupMissingFieldException(
                "'%s': security group rule '%s' has neither a 'GroupName' or "
                "'GroupId' field set." % (self, self._heat_resource_name)
            )
        if target_group not in self._context.heat_resource_stack:
            raise exceptions.SecurityGroupNotFoundException(
                "'%s': target security group '%s' for rule '%s' does not "
                "exist." % (self, target_group, self._heat_resource_name)
            )

        return target_group


class EC2SecurityGroupRuleEgressARMTranslator(
        BaseEC2SecurityGroupRuleARMTranslator):
    """ EC2SecurityGroupRuleEgressARMTranslator is the translator for CFN
    AWS::EC2::SecurityGroupIngress resources.

    It 'injects' the translated rule into the resulting ARM security group.
    """

    heat_resource_type = "AWS::EC2::SecurityGroupEgress"

    _rule_direction = "Outbound"

    _target_secgroup_field_name = "DestinationSecurityGroupId"

    def _get_target(self):
        """ _get_target returns the target security group of the rule.

        SecurityGroupIngress rules can specify the target group
        through the 'GroupId' field.
        """
        if 'GroupId' not in self._heat_resource.properties:
            raise exceptions.SecurityGroupMissingFieldException(
                "'%s': security group rule '%s' has no 'GroupId' field set." %
                (self, self._heat_resource_name)
            )

        target_group = self._heat_resource.properties["GroupId"]
        if target_group not in self._context.heat_resource_stack:
            raise exceptions.SecurityGroupNotFoundException(
                "'%s': target security group '%s' for rule '%s' does not "
                "exist." % (self, target_group, self._heat_resource_name)
            )

        return target_group
