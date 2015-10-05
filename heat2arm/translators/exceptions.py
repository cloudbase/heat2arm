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
    This module contains definitions for the base classes of all resource
    translation Exceptions which may be raised.
"""


class MissingFieldException(Exception):
    """ MissingFieldException is raised whenever a given Heat/CFN resource is
    missing a field which is mandatory for the translation process.
    """
    pass


class InvalidFieldException(Exception):
    """ InvalidFieldException is raised whenever a given Heat/CFN resource
    field contains an invalid value.
    """
    pass


class HeatResourceNotFoundException(Exception):
    """ HeatResourceNotFoundException is raised whenever a required resource is
    not found amongst the resources defined within the provided Heat template.
    """
    pass


class ARMResourceNotFoundException(Exception):
    """ ARMResourceNotFoundException is raised whenever a required ARM resource
    is not present post-initial translation.
    """
    pass
