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
    This module defines a number of exceptions used by the parser.
"""


class TemplateDataException(Exception):
    """ TemplateDataException is raised when a template does not contain the
    minimum required fields for it to be convertible.
    """
    pass


class FunctionArgumentException(Exception):
    """ FunctionArgumentException is raised when a templating language
    functions'arguments are incorrect.
    """
    pass


class FunctionApplicationException(Exception):
    """ FunctionApplicationException is raised when a templating language
    functions'application encounters an exception.
    """
    pass


class ResourceNameMissingException(Exception):
    """ ResourceNameMissingException is raised when a Resource defined in a
    template has no name.
    """
    pass


class ResourceTypeMissingException(Exception):
    """ ResourcePropertiesMissingException is raised when a resource defined in
    a template does not have the mandatory properties field in it.
    """
    pass
