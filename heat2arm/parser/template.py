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
    Contains the definition for the class of a Template.
"""

import yaml

from heat2arm.parser.cfn import FUNCTIONS as cfn_functions
from heat2arm.parser.cfn import RESOURCE_CLASS as cfn_resource_class
from heat2arm.parser.cfn import CFN_TEMPLATE_FIELDS as cfn_template_fields
from heat2arm.parser.hot import FUNCTIONS as heat_functions
from heat2arm.parser.hot import RESOURCE_CLASS as heat_resource_class
from heat2arm.parser.hot import HEAT_TEMPLATE_FIELDS as heat_template_fields


class Template(object):
    """ Template represents a template in all its entirety.
    It allows the resource and function parsers to access the parameters,
    variables and resource definitions defined within the template.

    When defined, it simply takes the string representing the template and
    loads all of its contents.
    """

    def __init__(self, template):
        """ A template object is created by passing in the string
        representing the template.

        It goes ahead and uses the standard yaml module to load the contents of
        the template and stores in its attributes the provided data.
        """
        # the classic fields of any template:
        self.parameters = None
        self.resources = None
        self.variables = {}
        self._template_fields = {}

        # the list of templating language functions which can be applied:
        self._functions = []

        # NOTE: considering JSON is a subset of YAML since the 1.2 version of
        # YAML's specification; we directly use the in-build yaml module for
        # parsing the input template.
        self._template_data = yaml.load(template)

        # check whether we're dealing with a CFN or a Heat template and define
        # the appropriate fields:
        if self._test_template_data(cfn_template_fields.values()):
            # then, load the CFN-style fields, functions and Resource class:
            self._template_fields = cfn_template_fields
            self._init_functions(cfn_functions)
            self._resource_class = cfn_resource_class
        elif self._test_template_data(heat_template_fields.values()):
            # then, load the Heat-style fields, functions and Resource class:
            self._template_fields = heat_template_fields
            self._init_functions(heat_functions)
            self._resource_class = heat_resource_class
        else:
            # else, rock bottom:
            raise Exception("Provided template data does not contain the"
                            "mandatory parameter and resource definitions"
                            "fields.")
        self._validate_template_data()

        # extract our required fields:
        self.parameters = self._template_data[self._template_fields[
            "parameters"
        ]]
        self.resources = self._template_data[self._template_fields[
            "resources"
        ]]
        self.variables = self._template_data.get(
            self._template_fields["variables"], {}
        )

        # NOTE: we pop out the outputs section of the template to ease parsing,
        # as it's useless to the translation process anyways:
        if self._template_fields["outputs"] in self._template_data:
            self._template_data.pop(self._template_fields["outputs"])

    def reduce_functions(self):
        """ reduce_functions reduces all the functions from within a template's
        data.
        """
        self._template_data = self._reduce_functions(self._template_data)

    def parse_resources(self):
        """ parse_resources instantiates all the resource classes from the
        resource data from within the template and returns their list.
        """
        resources = {}

        for name, data in self.resources.items():
            resources[name] = self._resource_class(name, data)

        return resources

    def _validate_template_data(self):
        """ _validate_template_data is a helper method which checks for the
        bare minimal set of fields for the data to be considered a template.
        """
        mandatories = {
            self._template_fields["parameters"],
            self._template_fields["resources"]
        }

        for field in mandatories:
            if field not in self._template_data:
                raise Exception("Missing template field '%s'." % field)

    def _test_template_data(self, expected_fields):
        """ _test_template_data is a helper method which, provided a list of
        expected fields, returns a boolean to signal whether or not the given
        data contains the required fields for it to count as a template.
        """
        template_keys = self._template_data.keys()

        return set(template_keys).issubset(expected_fields)

    def _init_functions(self, functions):
        """ _init_functions takes a list of classes which represent templating
        language functions and instantiates them.
        """
        self._functions = {func.name: func(self) for func in functions}

    def _apply_function(self, data):
        """ _apply_function is a helper method which, given a dict, determines
        whether it is a function application and returns the result of that
        application.
        """
        if len(data) != 1:
            # it means it's not a function and we return as-is:
            return data

        for k, v in data.items():
            # check if it is a function:
            if k in self._functions:
                # if so, check the validity of the arguments and apply it:
                return self._functions[k].apply(v)

        # else, it means it's not a function and we return as-is:
        return data

    def _reduce_functions(self, obj):
        """ _reduce_functions takes the whole template and recursively
        traverses it, applying all the templating functions depth-first.
        This is necessary to ensure consistency for outer-functions such
        as the join function to not be put off by another nested one.
        """
        is_list = isinstance(obj, list)
        is_dict = isinstance(obj, dict)

        if not (is_list or is_dict):
            # it means it's an uninteresting object and we can just return it:
            return obj

        if is_list:
            # apply to each element of the list:
            return map(self._reduce_functions, obj)

        if is_dict:
            # reduce each element of the dict before reducing the whole:
            for k, v in obj.items():
                obj[k] = self._reduce_functions(v)

            return self._apply_function(obj)
