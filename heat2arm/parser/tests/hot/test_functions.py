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
    This module contains tests for the Heat templating language functions.
"""

import unittest

from heat2arm.parser.common import exceptions
from heat2arm.parser.hot import functions
from heat2arm.parser.testing.hot_testing import (
    DUMMY_TEST_TEMPLATE,
    PROCESSED_TEST_TEMPLATE
)
from heat2arm.parser.testing.function_testing import (
    TestInput,
    FunctionTestCase
)


class TestJoinFunction(FunctionTestCase, unittest.TestCase):
    """ TestJoinFunction represents the set of test cases
    for testing Heat's list_join function.
    """

    _function_class = functions.HeatJoinListFunction

    _template_data = DUMMY_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test fail for anything but list with string and list of strings",
            [{}, [], 6],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test fail for anything but list with string and list of strings",
            ['first string is ok', [], 6],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test fail for anything but list with string and list of strings",
            ['first string is ok', ["second is bad list", {}, 5, 6]],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test basic scenario",
            ['', ["one", "two", "three"]],
            "onetwothree",
            None,
        ),
        TestInput(
            "test advanced scenario",
            ['separator', ["A", "B", "C"]],
            "AseparatorBseparatorC",
            None,
        )
    ]


class TestGetResourceFunction(FunctionTestCase, unittest.TestCase):
    """ TestGetResourceFunction represents the set of test cases for
    testing Heat's get_resource function.
    """

    _function_class = functions.HeatGetResourceFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test inexistent resource",
            "inexistent_resource",
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "simple resource reference",
            "dummy_resource",
            "dummy_resource",
            None
        )
    ]


class TestGetParameterFunction(FunctionTestCase, unittest.TestCase):
    """ TestGetParameterFunction represents the set of test cases for
    testing Heat's get_parameter function.
    """

    _function_class = functions.HeatGetParameterFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test inexistent parameter",
            "inexistent_parameter",
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test simple parameter reference",
            "simple_param",
            "simple_string",
            None
        ),
        TestInput(
            "test advanced parameter reference",
            "advanced_param",
            ["An", "unexpected", "list"],
            None
        ),
        TestInput(
            "test no default value parameter reference",
            "no_default",
            "no_default",
            None
        )
    ]


class TestGetAttrFunction(FunctionTestCase, unittest.TestCase):
    """ TestGetAttrFunction represents the set of tests applied
    to the Heat get_attr function.
    """

    _function_class = functions.HeatGetAttrFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test argument not a list",
            "random_thing",
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test argument list too short",
            ["random_thing"],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test simple attribute fetch",
            ["dummy_resource", "prop"],
            "val",
            None
        ),
        TestInput(
            "test advanced attribute get",
            ["dummy_resource", "nested_prop", "nested_list", 1, "key"],
            "value",
            None
        ),
        TestInput(
            "test inexistent resource",
            ["inexistent_resource", "inexistent_field"],
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test resource has no 'Properties' field",
            ["resource_param", "random_field"],
            None,
            exceptions.FunctionApplicationException
        )
    ]
