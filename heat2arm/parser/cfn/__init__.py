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
    This module contains definitions for CFN template processing.
"""

from heat2arm.parser.cfn import functions
from heat2arm.parser.cfn.constants import CFN_TEMPLATE_FIELDS
from heat2arm.parser.cfn.resource import CFNResource as RESOURCE_CLASS

FUNCTIONS = [
    functions.CFNBase64Function,
    functions.CFNFindInMapFunction,
    functions.CFNGetAttrFunction,
    functions.CFNJoinFunction,
    functions.CFNRefFunction,
]
