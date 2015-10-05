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
    This module contains general utility functions used in
    AutoScalingGroup translations.
"""


def seconds_to_iso_minutes(seconds):
    """ seconds_to_ISO_minutes is a helper function which, given a number of
    seconds; returns the string representation of those seconds; converted
    to minutes (and truncated!!!) according to the ISO 8601 time format.

    NOTE: It returns the period in minutes as a finer granularity
    is not permitted and a larger one is not required.
    """
    mins = int(int(seconds)/60)
    if mins < 1:
        mins = 1
    return "PT%sM" % (mins)


def create_avail_set_uri(avail_set_name):
    """ create_avail_set_uri is a helper function which; given the name of
    an availabilitySet, returns the expression which represents the unique
    Azure URI of that availabilitySet.
    """
    return ("[concat(resourceGroup().id, '/providers/Microsoft.Compute/"
            "availabilitySets/', variables('availabilitySetName_%s'))]"
            % avail_set_name)
