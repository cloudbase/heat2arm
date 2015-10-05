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
    This module contains for Heat Template Resource processing.
"""

import unittest

from heat2arm.parser.common import exceptions
from heat2arm.parser.hot.resource import HeatResource
from heat2arm.parser.hot.constants import HEAT_TEMPLATE_FIELDS
from heat2arm.parser.testing.resource_testing import (
    TestInput,
    ResourceTestCase
)


class TestHeatResource(ResourceTestCase, unittest.TestCase):
    """ TestHeatResource represents the set of tests to applied
    to HeatResource class creation.
    """

    _resource_class = HeatResource

    _field_names = HEAT_TEMPLATE_FIELDS

    _test_cases = [
        TestInput(
            "resource name missing",
            "",
            {},
            exceptions.ResourceNameMissingException
        ),
        TestInput(
            "'type' field missing",
            "test_resource",
            {},
            exceptions.ResourceTypeMissingException
        ),
        TestInput(
            "simple resource with no properties",
            "test_resource",
            {'type': "test_resource_type"},
            None
        ),
        TestInput(
            "simple resource with empty properties",
            "test_resource",
            {'type': "test_resource_type", 'properties': {}},
            None
        ),
        TestInput(
            "fully-blown resource",
            "test_resource",
            {
                'type': "test_resource_type",
                'properties': {
                    'some': "property",
                    'some_list':  ['example', 'list', 'property'],
                    'some_dict': {
                        'an': "example",
                        'dict': "property"
                    },
                    'yet_another': "property"
                }
            },
            None
        ),
    ]
