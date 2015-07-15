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
    Defines the Neutron Floating IP translator.
"""

from heat2arm.translators.networking.floating_ips.base_floating_ip import (
    BaseFloatingIPARMTranslator
)


class NeutronFloatingIPARMTranslator(BaseFloatingIPARMTranslator):
    """ NeutronFloatingIPARMTranslator is the translator associated to a
    Neutron floating IP range.
    """
    heat_resource_type = "OS::Neutron::FloatingIP"

    # NOTE: the following are inherited from BaseFloatingIPARMTranslator:
    #   - get_parameters.
    #   - get_variables.
    #   - get_resource_data.
