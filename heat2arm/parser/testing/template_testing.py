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
    This module contains various definitions which aid in overall Template
    parsing behavior testing.
"""

import collections
import logging
import yaml

from heat2arm.parser.common.resource import Resource
from heat2arm.parser.template import Template
from heat2arm.parser.testing.testutils import recursive_dict_search

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("test_template")


# TemplateParsingTestInput is a data structure used for testing the behavior of
# the Template parsing logic against invalid input.
# It contains the following fields:
#   - template_data - the raw template data to be used for the test
#   - expected_exception - the Exception class expected to be raised
TemplateParsingTestInput = collections.namedtuple(
    "TemplateParsingTestInput",
    "description template_data expected_exception"
)


class TemplateParsingTestCase(object):
    """ FunctionApplicationTestCase represents the set of tests which ensure
    the proper behavior for template parsing.

    It is meant to be inherited alongside unittest.TestCase.
    """

    # _field_names is a dict containing the mapping between common field
    # types and their names within a respective template format:
    _field_names = {}

    # _function_application_test_data is the raw template data
    # to be used in test_functions_get_applied:
    _function_application_test_data = ""

    # _resource_parsing_test_data is the raw template data to be used as
    # input in test_parse_resource:
    _resource_parsing_test_data = ""

    # _template_parsing_test_data is a list of TemplateParsingTestInputs to be
    # used as inputs in test_parsing_behavior:
    _template_parsing_test_data = []

    def test_functions_get_applied(self):
        """ test_functions_get_applied tests that running the function
        application on a Template's data reduces all available functions.
        """
        LOG.debug(
            "testing function application correctness on '%s'.",
            self._function_application_test_data
        )
        temp = Template(self._function_application_test_data)
        temp.reduce_functions()

        # for each registered templating function (which are considered to
        # behave correctly, as they have their separate tests), ensure that
        # there is no unapplied instance of it in the resulting template:
        for func_name in temp._functions:
            LOG.debug(
                "checking for unapplied function '%s' in '%s'.",
                func_name,
                temp._template_data
            )
            self.assertFalse(recursive_dict_search(
                temp._template_data, func_name))

    def test_parse_resources(self):
        """ test_parse_resources tests that running the resource extraction
        procedure will yield the appropriate set of resources:
        """
        LOG.debug(
            "testing resource parsing on '%s'",
            self._resource_parsing_test_data
        )

        temp = Template(self._resource_parsing_test_data)
        parsed_resources = temp.parse_resources()

        input_resources = yaml.load(self._resource_parsing_test_data)[
            self._field_names["resources"]
        ]

        # ensure all the resources defined in the input template have a
        # corresponding Resource instance created for them:
        for res_name, res_data in input_resources.items():
            self.assertTrue(res_name in parsed_resources)
            self.assertDictEqual(
                parsed_resources[res_name].properties,
                res_data.get(self._field_names["properties"], {})
            )

    def test_invalid_data(self):
        """ test_invalid_data tests the behavior of the Template parsing logic
        agains flawed or incomplete templates.
        """
        for test_input in self._template_parsing_test_data:
            LOG.debug(
                "testing Template parsing reaction to invalid data '%s': %s.",
                test_input.template_data,
                test_input.description
            )

            with self.assertRaises(test_input.expected_exception):
                Template(test_input.template_data)
