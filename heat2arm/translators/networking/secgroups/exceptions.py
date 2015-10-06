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
    This module contains definitions for specific exceptions which may
    be encountered during the translation of various security group resources.
"""

from heat2arm.translators import exceptions


class SecurityGroupMissingFieldException(exceptions.MissingFieldException):
    """ SecurityGroupMissingFieldException is raised whenever a missing
    field is not found during the translation of a network security group.
    """
    pass


class SecurityGroupInvalidFieldException(exceptions.InvalidFieldException):
    """ SecurityGroupInvalidFieldException is raised whenever a defined
    security group has an invalid value within one of its fields.
    """
    pass
