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
    Contains the definitions of the volume attachment translators.
"""

from heat2arm.translators.base import BaseHeatARMTranslator


class CinderVolumeAttachmentARMTranslator(BaseHeatARMTranslator):
    """ CinderVolumeAttachmentARMTranslator is the translator for
    Cinder volume attachments.

    It is completely no-op; as volume attachments in Azure are specified within
    the bodies of the instances; and this this functionality is implemented in
    the instance translatos.
    """
    heat_resource_type = "OS::Cinder::VolumeAttachment"
    arm_resource_type = ""


class EBSVolumeAttachmentARMTranslator(BaseHeatARMTranslator):
    """ EBSVolumeAttachmentARMTranslator is the translator for
    EBS volume attachments.

    It is completely no-op; as volume attachments in Azure are specified within
    the bodies of the instances; and this this functionality is implemented in
    the instance translatos.
    """
    heat_resource_type = "AWS::EC2::VolumeAttachment"
    arm_resource_type = ""
