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
    This module contains the definitions for the major functions
    of a heat template.
"""

from heat2arm.parser.common import functions


class HeatGetResourceFunction(functions.RefFunction):
    """ HeatGetResourceFunction implements the functionality of the
    get_resource Heat template function.

    It takes the form:

        " get_resource: resource_name "

    NOTE: Heat has a complicated logic associated to this function; with
    get_resource returning a resource-specific item. For our intents and
    purposes, we only return the referenced resource's name.
    """
    name = "get_resource"


class HeatGetParameterFunction(functions.RefFunction):
    """ HeatGetParameterFunction implements the functionality of the
    get_parameter Heat template function.

    It takes the form:

        " get_param: parameter_name "

    NOTE: All parameters are expected to have a 'default' field set.
    """
    name = "get_param"
    _param_default_field_name = "default"


class HeatJoinListFunction(functions.JoinFunction):
    """ HeatJoinListFunction implements the functionality of the list_join Heat
    template function.

    It takes the form:

        " list_join: [ 'separator', ['arg1', 'arg2', ... ] ] "
    """
    name = "list_join"


class HeatGetAttrFunction(functions.GetAttrFunction):
    """ HeatGetAttrFunction implements the functionality of the get_attr
    Heat template function.

    It takes the form:

        " get_attr: ['resource_name', 'field_name', ...] "
    """
    name = "get_attr"
    _properties_field_name = "properties"
