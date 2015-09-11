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
    This module contains tests for the CFN templating language functions.
"""

import unittest

from heat2arm.parser.common import exceptions
from heat2arm.parser.cfn import functions
from heat2arm.parser.testing.cfn_testing import (
    DUMMY_TEST_TEMPLATE,
    PROCESSED_TEST_TEMPLATE
)
from heat2arm.parser.testing.function_testing import (
    TestInput,
    FunctionTestCase
)


class TestBase64Function(FunctionTestCase, unittest.TestCase):
    """ TestBase64Function represents the set of test cases for
    testing CFN's Base64 function.
    """

    _function_class = functions.CFNBase64Function

    _template_data = DUMMY_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test fail for anything but string as argument",
            ["not", "a", "string"],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test check equality of return value",
            "some string",
            "some string",
            None
        )
    ]


class TestJoinFunction(FunctionTestCase, unittest.TestCase):
    """ TestJoinFunction represents the set of test cases
    for testing CFN's Join function.
    """

    _function_class = functions.CFNJoinFunction

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


class TestRefFunction(FunctionTestCase, unittest.TestCase):
    """ TestRefFunction represents the set of test cases for
    testing CFN's Ref function.
    """

    _function_class = functions.CFNRefFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test inexistent parameter or resource",
            "InexistentParameter",
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test simple parameter reference",
            "SimpleParam",
            "SimpleString",
            None
        ),
        TestInput(
            "test advanced parameter reference",
            "AdvancedParam",
            ["An", "unexpected", "list"],
            None
        ),
        TestInput(
            "test no default value parameter reference",
            "NoDefault",
            "NoDefault",
            None
        ),
        TestInput(
            "simple resource reference",
            "DummyResource",
            "DummyResource",
            None
        ),
        TestInput(
            "test parameters have proprity",
            "ResourceParam",
            "prioritised",
            None
        )
    ]


class TestGetAttFunction(FunctionTestCase, unittest.TestCase):
    """ TestGetAttFunction represents the set of tests applied
    to the CFN GetAtt function.
    """

    _function_class = functions.CFNGetAttrFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test argument not a list",
            "RandomThing",
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test argument list too short",
            ["RandomThing"],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test simple attribute fetch",
            ["DummyResource", "Prop1"],
            "value 1",
            None
        ),
        TestInput(
            "test advanced attribute get",
            ["DummyResource", "NestedProp", "NestedList", 1, "key1"],
            "val1",
            None
        ),
        TestInput(
            "test inexistent resource",
            ["InexistentResource", "WithInexistentField"],
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test resource has no 'Properties' field",
            ["ResourceParam", "RandomField"],
            None,
            exceptions.FunctionApplicationException
        )
    ]


class TestFindInMapFunction(FunctionTestCase, unittest.TestCase):
    """ TestFindInMapFunction represents the set of test cases
    to be applied to CFN's FindInMap function.
    """

    _function_class = functions.CFNFindInMapFunction

    _template_data = PROCESSED_TEST_TEMPLATE

    _test_cases = [
        TestInput(
            "test invalid argument type",
            "not a list",
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test invalid argument list elements",
            ["a string", 5, 34.2],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test invalid argument list length",
            ["one", "two", "three", "too many..."],
            None,
            exceptions.FunctionArgumentException
        ),
        TestInput(
            "test inexistent mapping",
            ["MappingThatDoesNotExist", "SomeKey", "SomeVal"],
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test get bad mapping element",
            ["ExampleMapping", "bad", "something"],
            None,
            exceptions.FunctionApplicationException
        ),
        TestInput(
            "test map get",
            ["ExampleMapping", "good", "goodval"],
            "some value",
            None
        )
    ]
