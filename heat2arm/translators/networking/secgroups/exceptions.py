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
    This module cotains definitions for various exception classes which are
    raised during the translation process of Security groups.
"""

from heat2arm.translators import exceptions


class SecurityGroupMissingFieldException(exceptions.MissingFieldException):
    """ SecurityGroupMissingFieldException is raised when a required field from
    a translated security group is missing.
    """
    pass


class SecurityGroupInvalidFieldException(exceptions.InvalidFieldException):
    """ SecurityGroupInvalidFieldException is raised when the value of a field
    of a security group that is undergoing the translation process is invalid.
    """
    pass


class SecurityGroupNotFoundException(exceptions.HeatResourceNotFoundException):
    """ SecurityGroupNotFoundException is raised whenever a referenced security
    group is not found.
    """
    pass
