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
    This module contains declarations useful for the testing of templating
    language functions.
"""

import collections
import logging

from heat2arm.parser.template import Template


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("test_functions")


# TestInput is a type representing the data to be
# used as input for tests. Its fields are:
#   - description - short description of the test input.
#   - input - the input Function.apply() will be called on.
#   - output - the output expected.
#   - exception - the exception expected to be raised.
TestInput = collections.namedtuple(
    'TestInput',
    'description input output exception'
)


class FunctionTestCase(object):
    """ FunctionTestCase represents the class of all test cases
    involving templating language functions.

    It is meant to be inherited alongside unittest.TestCase in
    the specific TestCases themselves.
    """

    # _function is the Function class whose instances will
    # represent the object of the test cases.
    _function_class = None

    # _test_cases is a list of TestInputs to be tested.
    _test_cases = []

    # _template_data is the template data to be passed to the template
    # which is created for the Function class.
    _template_data = "{}"

    def setUp(self):
        self._function = self._function_class(Template(self._template_data))

    def test(self):
        # iterate through all the provided _test_cases and:
        #    - if an expected output is provided; test against it.
        #    - if an expected Exception is provided, check for it.
        for test_case in self._test_cases:
            LOG.debug(
                "Running '%s' on '%s': %s.",
                self._function.name,
                test_case.input,
                test_case.description
            )
            # first, check if an ouput is expected:
            if test_case.output:
                self.assertEqual(
                    self._function.apply(
                        test_case.input
                    ),
                    test_case.output
                )
                continue
            # else, it means that an assertRaises is required.
            elif test_case.exception:
                with self.assertRaises(test_case.exception):
                    self._function.apply(test_case.input)
                    continue
            else:
                raise Exception("Invalid test case; must specify either"
                                "desired output or checked exception.")
