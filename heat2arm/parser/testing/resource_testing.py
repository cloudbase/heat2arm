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
    This module contains definitions useful for the testing of template
    resource extraction.
"""

import collections
import logging


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger("test_resources")


# TestInput is a data structure representing the data to be used as input for
# tests. Its fields are:
#   - description - short description of the test case
#   - resource_name - name of the resource
#   - resource_data - the data associated to the resource
#   - exception - the exception which is expected to be raised, if applicable
TestInput = collections.namedtuple(
    'TestInput',
    'description resource_name resource_data exception'
)

class ResourceTestCase(object):
    """ ResourceTestCase represents the class of all test cases involving
    the Resource class.

    It is meant to be inherited alongside unittest.TestCase in the TestCases
    for the specific resource types (Heat or CFN) themselves.
    """

    # _resource_class is the Resource class we are testing against:
    _resource_class = None

    # _field_names is a dict representing the names of keys
    # of the resource data.
    _field_names = {}

    # _test_cases is a list of TestInputs to be tested:
    _test_cases = []

    def test(self):
        # iterate through all the provided _test_cases and:
        #   - if an Exception was provided, check that it has been raised
        #   - if no Exception is expected, check that the fields get assigned.
        for test_case in self._test_cases:
            LOG.debug(
                "Testing '%s' on { %s : %s }: '%s'",
                self._resource_class.__name__,
                test_case.resource_name,
                test_case.resource_data,
                test_case.description
            )

            # first, check for the exception case:
            if test_case.exception:
                with self.assertRaises(test_case.exception):
                    self._resource_class(
                        test_case.resource_name,
                        test_case.resource_data
                    )
            else:
                # else; ensure the resource was properly created:
                res = self._resource_class(
                    test_case.resource_name,
                    test_case.resource_data
                )

                # check the mandatory name and type properties:
                self.assertEqual(res.name, test_case.resource_name)
                self.assertEqual(
                    res.type, test_case.resource_data[
                        self._field_names["type"]
                    ]
                )

                # check for the optional properties and meta fields:
                self.assertDictEqual(
                    res.properties,
                    test_case.resource_data.get(
                        self._field_names["properties"], {}
                    )
                )
                if "meta" in self._field_names:
                    self.assertDictEqual(
                        res.meta, test_case.resource_data.get(
                            self._field_names["meta"], {}
                        )
                    )
