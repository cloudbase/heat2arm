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
    This module contains tests for Heat template parsing mechanics.
"""

import unittest
from yaml.parser import ParserError

from heat2arm.parser.common.exceptions import (
    TemplateDataException
)
from heat2arm.parser.hot.constants import HEAT_TEMPLATE_FIELDS
from heat2arm.parser.testing.hot_testing import COMPLETE_TEST_TEMPLATE
from heat2arm.parser.testing.template_testing import (
    TemplateParsingTestInput,
    TemplateParsingTestCase
)


class HeatTemplateParsingTestCase(TemplateParsingTestCase, unittest.TestCase):
    """ HeatTemplateParsingTestCase respresents a set of tests which ensure the
    proper parsing of Heat Templates.
    """

    _field_names = HEAT_TEMPLATE_FIELDS

    _function_application_test_data = COMPLETE_TEST_TEMPLATE

    _resource_parsing_test_data = COMPLETE_TEST_TEMPLATE

    _template_parsing_test_data = [
        TemplateParsingTestInput(
            "test empty template",
            "",
            TemplateDataException
        ),
        TemplateParsingTestInput(
            "test invalid JSON",
            "some : [random] _ ness )",
            ParserError
        ),
        TemplateParsingTestInput(
            "not a valid template",
            "it's just a string...",
            TemplateDataException
        ),
        TemplateParsingTestInput(
            "no relevant fields provided",
            "{ 'some':  'random_dict' }",
            TemplateDataException
        ),
        TemplateParsingTestInput(
            "no 'parameters' field provided",
            "{ 'resources': 'they should be here...' }",
            TemplateDataException
        ),
        TemplateParsingTestInput(
            "no 'resources' field provided",
            "{ 'parameters': 'some_random_parameters_data' }",
            TemplateDataException
        ),
    ]
