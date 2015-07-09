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

from heat2arm.constants import ARM_API_2015_05_01_PREVIEW
from heat2arm.translators.base import BaseHeatARMTranslator


class BaseSecurityGroupARMTranslator(BaseHeatARMTranslator):
    """ BaseSecurityGroupARMTranslator is a specialised verions of the
    BaseHeatARMTranslator which provides some sensible default
    implementations to be used in inheriting translators.
    """
    arm_resource_type = "Microsoft.Network/networkSecurityGroups"

    def _get_base_secgroup_header(self):
        """ _get_base_secgroup_header is a helper method which returns a dict
        containing the standard set of properties of an ARM
        Security Group declaration.
        """
        return {
            "apiVersion": ARM_API_2015_05_01_PREVIEW,
            "type": self.arm_resource_type,
            "name": ("[variables('secGroupName_%s')]" %
                     self._heat_resource.name),
            "location": "[variables('location')]",
        }
