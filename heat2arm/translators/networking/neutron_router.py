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
    Contains base no-op translations for Neutron routers and interfaces.
"""

from heat2arm.translators.base import BaseHeatARMTranslator


class NeutronRouterARMTranslator(BaseHeatARMTranslator):
    """ NeutronRouterARMTranslator is the translator for a Neutron router.

    It has no direct Azure equivalent; so its translation is thus empty.
    """
    heat_resource_type = "OS::Neutron::Router"

    # No direct ARM resource translation
    arm_resource_type = ""


class NeutronRouterInterfaceARMTranslator(BaseHeatARMTranslator):
    """ NeutronRouterInterfaceARMTranslator is the translator
    for a Neutron router resource.

    It has no direct Azure equivalent; so its translation is thus empty.
    """
    heat_resource_type = "OS::Neutron::RouterInterface"

    # No direct ARM resource translation
    arm_resource_type = ""
