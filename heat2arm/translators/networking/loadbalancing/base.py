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
    This module contains the definition of the base load balancer translator.
"""

from heat2arm.config import CONF
from heat2arm.translators.base import BaseHeatARMTranslator
from heat2arm.translators.networking.loadbalancing import exceptions


class BaseLoadBalancerARMTranslator(BaseHeatARMTranslator):
    """ BaseLoadBalancerARMTranslator contains all the functionality common to
    the translation of both AWS and Heat load balancers.
    """

    heat_resource_type = ""
    arm_resource_type = "Microsoft.Network/loadBalancers"

    # _mandatory_rule_fields is the list of field names which must be present
    # within the definition of any redirect rule defined for the translator:
    _mandatory_rule_fields = []

    def get_variables(self):
        """ get_variables returns the dict of variables used
        in the LoadBalancer's translation.
        """
        super(BaseLoadBalancerARMTranslator, self).get_variables()

        return {
            "loadBalancerName_%s" % self._heat_resource_name:
                "loadBalancer_%s" % self._heat_resource_name,
            "frontendIPConfigID_%s" % self._heat_resource_name:
                "[concat(resourceId('Microsoft.Network/loadBalancers', "
                "variables('loadBalancerName_%s')),'/frontendIPConfigurations"
                "/frontendIP_%s')]" % ((self._heat_resource_name, ) * 2)
        }

    def get_dependencies(self):
        """ get_dependencies returns the list of the resources
        this load balancer directly depends on.
        """
        return [
            "[concat('Microsoft.Network/publicIPAddresses/', "
            "variables('publicIPName_%s'))]" % self._heat_resource_name
        ]

    def get_resource_data(self):
        """ get_resource_data returns the dict representing the data of the
        resource's translation. It is directly serializable into JSON.
        """
        super(BaseLoadBalancerARMTranslator, self).get_resource_data()

        return [{
            "apiVersion": CONF.arm_api_version,
            "type": self.arm_resource_type,
            "name": "[variables('loadBalancerName_%s')]" %
                    self._heat_resource_name,
            "location": "[variables('location')]",
            "dependsOn": self.get_dependencies(),
            "properties": {
                "frontendIPConfigurations": [{
                    "name": "frontendIP_%s" % self._heat_resource_name,
                    "properties": {
                        "publicIPAddress": {
                            # TODO: ok?
                            "id":
                                "[resourceId('Microsoft.Network/publicIP"
                                "Addresses',variables('publicIPName_%s'))]" %
                                self._heat_resource_name
                        }
                    }
                }],
                "backendAddressPools": [{
                    "name": "backendAddressPool_%s" % self._heat_resource_name
                }],
                "inboundNatRules": self._get_nat_rules(),
            }
        }]

    def update_context(self):
        """ update_context updates the translation context with all the details
        representing the LoadBalancer's translation.
        """
        super(BaseLoadBalancerARMTranslator, self).update_context()

        # first; create the new public IP resource:
        pub_ip_name = 'publicIPName_%s' % self._heat_resource_name

        self._context.add_variables({
            pub_ip_name: "publicIP_%s" % self._heat_resource_name
        })

        self._context.add_parameters({
            "dnsNameForLoadBalancerPublicIP_%s" % self._heat_resource_name: {
                "type": "string",
                "metadata": {
                    "description": "Unique DNS name for the LoadBalancer "
                                   "'%s''s public IP." %
                                   self._heat_resource_name
                }
            }
        })

        self._context.add_resource({
            "apiVersion": CONF.arm_api_version,
            "name": "[variables('%s')]" % pub_ip_name,
            "type": "Microsoft.Network/publicIPAddresses",
            "location": "[variables('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "dnsSettings": {
                    "domainNameLabel":
                        "[parameters('dnsNameForLoadBalancerPublicIP_%s')]" % (
                            self._heat_resource_name
                        )
                }
            }
        })

        # now, we must go ahead and find the required NIC:
        nic = self._context.get_arm_resource({
            "type": "Microsoft.Network/networkInterfaces",
            "name": self._get_nic()
        })

        # and add the necessary information to it:
        # TODO(aznashwan): would extension work here?
        nic["properties"]["ipConfigurations"][0][
            "loadBalancerBackendAddressPools"
        ] = [{
            "id": "[concat(resourceId('Microsoft.Network/loadBalancers', "
                  "variables('loadBalancerName_%s')), '/backendAddressPools/"
                  "backendAddressPool_%s')]" % ((self._heat_resource_name, ) * 2)
        }]


        nic["properties"]["ipConfigurations"][0][
            "loadBalancerInboundNatRules"
        ] = []
        for rule in self._get_nat_rules():
            nic["properties"]["ipConfigurations"][0][
                "loadBalancerInboundNatRules"
            ].append({
                "id": "[concat(resourceId('Microsoft.Network/loadBalancers', "
                      "variables('loadBalancerName_%s')), "
                      "'/inboundNatRules/%s'" % (
                          self._heat_resource_name, rule["name"]
                      )
            })

        nic["properties"]["ipConfigurations"][0][
            "loadBalancerBackendAddressPools"
        ] = [{
            "id": "[concat(resourceId('Microsoft.Network/loadBalancers', "
                  "variables('loadBalancerName_%s')), '/backendAddressPools/"
                  "backendAddressPool_%s')]" % ((self._heat_resource_name, ) * 2)
        }]


    def _get_nic(self):
        """ _get_nic is a helper method which returns the nic which will be
        subject to the load balancing. The nic is guaranteed to exist (if none
        are specified for a VM we add our own by default anyhow).

        NOTE: it is meant to be called after the initial translation step.
        """
        pass

    def _get_nat_rules(self):
        """ _get_nat_rules is a helper method which returns the full data
        associated to the resulting NAT rules on Azure.

        NOTE: it is no-op and should be overriden in all inheriting classes.
        """
        return []

    def _check_rule(self, rule):
        """ _check_rule is a helper method which, given the dict representing
        the data of a rule to be translated, validates that all the required
        fields are present.
        """
        for field in self._mandatory_rule_fields:
            if field not in rule:
                raise exceptions.LoadBalancerMissingFieldException(
                    "'%s': rule '%s' has no '%s' field." % (
                        self, rule, field
                    )
                )
