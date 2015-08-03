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

from heat2arm import constants
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseSecurityGroupARMTranslator(BaseHeatARMTranslator):
    """ BaseSecurityGroupARMTranslator is a specialised verions of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to be used in inheriting translators.
    """
    arm_resource_type = "Microsoft.Network/networkSecurityGroups"

    def _get_rules(self):
        """ _get_rules is a helper method which returns a list of all
        the resulting ARM security group rules to be created
        following the translation.

        NOTE: this is stubbed and must be implemented in all inheriting classes.
        """
        return []

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
        return [{
            "apiVersion": constants.ARM_API_VERSION,
            "type": self.arm_resource_type,
            "name": ("[variables('secGroupName_%s')]" %
                     self._heat_resource.name),
            "location": "[variables('location')]",
            "properties": {
                "securityRules": self._get_rules()
            }
        }]
