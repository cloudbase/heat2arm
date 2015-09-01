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
    Contains the definitions for the two main functions of this package.
"""

from heat2arm.parser.template import Template


def parse_template(template):
    """ parse instantiates a Template object with the provided string contents
    of the template and returns a dict of all the resources defined within it.
    """
    temp = Template(template)
    temp.reduce_functions()
    return temp.parse_resources()


def parse_file(filepath):
    """ parse_file loads the contents of the specified file and calls
    parse_template on it.
    """
    with open(filepath) as file:
        return parse_template(file.read())
