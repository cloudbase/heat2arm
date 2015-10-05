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
    Contains definitions of general constants found in all Heat templates.
"""

# HEAT_TEMPLATE_FIELDS represents the mapping between field types and field
# names which are characteristic of Heat templates.
HEAT_TEMPLATE_FIELDS = {
    "description": "description",
    "variables": "",  # TODO
    "parameters": "parameters",
    "type": "type",
    "meta": "",
    "properties": "properties",
    "resources": "resources",
    "aws_temp_format_version": "",
    "heat_temp_format_version": "heat_template_version",
    "outputs": "outputs"
}
