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
    This module contains definitions for CFN template functions.
"""

from heat2arm.parser.common import functions
from heat2arm.parser.cfn.constants import CFN_TEMPLATE_DEFAULTS


class CFNRefFunction(functions.RefFunction):
    """ CFNRefFunction implements the CFN template Ref function.

    It takes the form:

        " 'Ref': '(ResourceName|ParameterName)' "

    NOTE: in CFN, 'Ref' is used both for accessing parameters and referencing
    resources. For parameter accessing, it logs an exception if the parameter
    does not have a 'Default' field set. In the case of resource referencing,
    Heat has a complex mechanism for determining the appropriate result per
    resource. We do not require such behavior and simply return the referenced
    resource's name as provided.
    """
    name = "Ref"
    _param_default_field_name = "Default"


class CFNJoinFunction(functions.JoinFunction):
    """ CFNJoinFunction implements the CFN template Join function.

    It takes the form:

        " 'Fn::Join': [ 'Separator', [ 'arg1', 'arg2', ... ] ] "
    """
    name = "Fn::Join"


class CFNBase64Function(functions.Base64Function):
    """ CFNBase64Function implements the CFN template Base64 function.

    It takes the form:

        " 'Fn::Base64': 'String' "
    """
    name = "Fn::Base64"


class CFNGetAttrFunction(functions.GetAttrFunction):
    """ CFNGetAttrFunction implements the CFN template GetAtt function.

    It takes the form:

        " 'Fn::GetAtt': ['ResourceName', 'FieldName', ...] "
    """
    name = "Fn::GetAtt"
    _properties_field_name = "Properties"
    _exceptions = CFN_TEMPLATE_DEFAULTS


class CFNFindInMapFunction(functions.MapFindFunction):
    """ CFNFindInMapFunction implements the CFN template FindInMap function.

    It takes the form:

        " 'Fn::FindInMap' ['Mapping', 'Key', 'Value' ] "
    """
    name = "Fn::FindInMap"
