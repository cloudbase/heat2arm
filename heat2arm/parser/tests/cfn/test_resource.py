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
    This module contains tests for CFN Resource creation.
"""

import unittest

from heat2arm.parser.common import exceptions
from heat2arm.parser.cfn.constants import CFN_TEMPLATE_FIELDS
from heat2arm.parser.cfn.resource import CFNResource
from heat2arm.parser.testing.resource_testing import (
    TestInput,
    ResourceTestCase
)


class TestCFNResource(ResourceTestCase, unittest.TestCase):
    """ TestCFNResource represents the set of tests to applied
    to CFNResource class creation.
    """

    _resource_class = CFNResource

    _field_names = CFN_TEMPLATE_FIELDS

    _test_cases = [
        TestInput(
            "resource name missing",
            "",
            {},
            exceptions.ResourceNameMissingException
        ),
        TestInput(
            "'Type' field missing",
            "TestResource",
            {},
            exceptions.ResourceTypeMissingException
        ),
        TestInput(
            "simple resource with no properties",
            "TestResource",
            {'Type': "TestResourceType"},
            None
        ),
        TestInput(
            "simple resource with empty properties",
            "TestResource",
            {'Type': "TestResourceType", 'Properties': {}},
            None
        ),
        TestInput(
            "fully-blown resource",
            "TestResource",
            {
                'Type': "TestResourceType",
                'Metadata': {
                    'Some': {
                        'Example': "metadata"
                    }
                },
                'Properties': {
                    'Some': "Property",
                    'SomeList':  ['example', 'list', 'property'],
                    'SomeDict': {
                        'an': "example",
                        'dict': "property"
                    },
                    'YetAnother': "Property"
                }
            },
            None
        ),
    ]
