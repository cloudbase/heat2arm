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


class BaseVolumeAttachmentTranslator(BaseHeatARMTranslator):
    """ BaseVolumeAttachmentTranslator is the translator for volume
    attachment-like resources. It does not result in any translated resource,
    as volumes on Azure are directly declared within the body of the instance.
    """
    def _get_instance_name(self):
        """ _get_instance_name is a helper method which returns the name of the
        instance the volume will be attached to.

        It is stubbed and shoul be implemented by inheriting classes.
        """
        pass

    def _get_volume_name(self):
        """ _get_volume_name is a helper method which returns the name of the
        volume to be attached.

        It is stubbed and shoul be implemented by inheriting classes.
        """
        pass

    def update_context(self):
        """ update_context goes ahead and add the necessary volume declaration
        to the required instance.
        """
        volume_name = self._get_volume_name()

        res = self._context.get_resource({
            "type": "Microsoft.Compute/virtualMachines",
            "name":  "[variables('vmName_%s')]" % self._get_instance_name()
        })

        if "dataDisks" not in res["properties"]["storageProfile"]:
            res["properties"]["storageProfile"]["dataDisks"] = []

        res["properties"]["storageProfile"]["dataDisks"].append({
            "name": volume_name,
            "diskSizeGB": "[parameters('size_%s')]" %
                          volume_name,
            "lun": len(res["properties"]["storageProfile"]["dataDisks"]),
            "vhd": {
                "Uri": "[variables('diskUri_%s')]" %
                       volume_name,
                },
            "createOption": "Empty"
        })


class CinderVolumeAttachmentARMTranslator(BaseVolumeAttachmentTranslator):
    """ CinderVolumeAttachmentARMTranslator is the translator for
    Cinder volume attachments.
    """
    heat_resource_type = "OS::Cinder::VolumeAttachment"
    arm_resource_type = ""

    # NOTE: update_context is inherited from BaseVolumeAttachmentTranslator.

    def _get_volume_name(self):
        """ _get_volume_name returns the name of the Cinder volume
        referred to by the attachment.
        """
        return self._heat_resource.properties.data["volume_id"].args

    def _get_instance_name(self):
        """ _get_instance_name returns the name of the Nova server
        referred to by the attachment.
        """
        return self._heat_resource.properties.data["instance_uuid"].args


class EBSVolumeAttachmentARMTranslator(BaseVolumeAttachmentTranslator):
    """ EBSVolumeAttachmentARMTranslator is the translator for
    EBS volume attachments.
    """
    heat_resource_type = "AWS::EC2::VolumeAttachment"
    arm_resource_type = ""

    # NOTE: update_context is inherited from BaseVolumeAttachmentTranslator.

    def _get_volume_name(self):
        """ _get_volume_name returns the name of the EBS volume
        referred to by the attachment.
        """
        return self._heat_resource.properties.data["VolumeId"].args

    def _get_instance_name(self):
        """ _get_instance_name returns the name of the EC2 instance
        referred to by the attachment.
        """
        return self._heat_resource.properties.data["InstanceId"].args
