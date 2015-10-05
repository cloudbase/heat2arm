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
    This module contains the translator for an AWS ScalingPolicy.
"""

from heat2arm.translators.base import BaseHeatARMTranslator


class AWSScalingPolicyARMTranslator(BaseHeatARMTranslator):
    """ AWSScalingPolicyARMTranslator is the translator for an
    AWS::AutoScaling::ScalingPolicy.

    The logic for processing ScalingPolicies is wholly included in the
    AutoScalingGroup translator as the former is so dependant of the latter.
    As a result, this translator is completely no-op.
    """
    pass
