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
    Contains the definition for the EC2 EBS volume translator.
"""

from heat2arm.translators.storage.volumes.base_volume import (
    BaseVolumeARMTranslator
)


class EBSVolumeARMTranslator(BaseVolumeARMTranslator):
    """ EBSVolumeTranslator is the translator for AWS EC2
    Elastic Block Storage volumes.
    """
    heat_resource_type = "AWS::EC2::Volume"
    arm_resource_type = ""

    # NOTE: the following are inherited from BaseVolumeARMTranslator:
    #   - get_parameters
    #   - get_variables
