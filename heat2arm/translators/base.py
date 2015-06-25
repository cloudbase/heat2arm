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


class BaseHeatARMTranslator(object):
    heat_resource_type = None
    arm_resource_type = None

    def __init__(self, heat_resource):
        self._heat_resource = heat_resource
        self._name = self._heat_resource.name

    def get_parameters(self):
        return {}

    def get_variables(self):
        return {}

    def get_dependencies(self):
        return []

    def get_resource_data(self):
        return []


def get_ref_heat_resource(heat_resource, property_name):
    resource_name = heat_resource.properties.data[property_name].args
    return heat_resource.stack[resource_name]
