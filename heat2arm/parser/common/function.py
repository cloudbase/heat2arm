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
    Contains the definition for the base class of all templating
    language functions.
"""


class Function(object):
    """ Function is the base class of templating language functions.
    """

    # the name of the function:
    name = ""

    def __init__(self, template):
        """ A function is instantiated with the general Template for
        access to the various other variables, parameters and resources
        within it.
        """
        self._template = template

    def _check_args(self, args):
        """ _check_args is an internal helper method to ensure that the
        provided arguments are correct.

        It sould be implemented by inheriting classes which required any
        argument-checking done pre-emptively.
        """
        pass

    def apply(self, args):
        """ apply applies the function transmormation to the given set
        of data and returns the result.

        apply expects that only the actual args be provided as a parameter.

        Example:

            " 'Function.name': [[ 'arg1', 'arg2', 'arg3' ]] "

        Args should only contain the list of arguments.

        It should be implemented by all inheriting classes.
        """
        pass
