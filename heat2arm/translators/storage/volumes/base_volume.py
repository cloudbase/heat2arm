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
    Contains the base definition for volume resource translators.
"""

from heat2arm.translators.base import BaseHeatARMTranslator


class BaseVolumeARMTranslator(BaseHeatARMTranslator):
    """ BaseVolumeTranslator is the base implementation of all
    data volume resource translators.

    Stand-alone data volumes don't have a direct Azure equivalent;
    they will be modeled as simple storage blobs.
    """
    heat_resource_type = None
    arm_resource_type = None

    def __init__(self, heat_resource, context):
        super(BaseVolumeARMTranslator, self).__init__(heat_resource, context)
        self._context.set_storage_account_required()

    def get_parameters(self):
        """ get_parameters returns the dict with the size parameter that all
        volumes must have.
        """
        return {
            self._make_var_name("size"): {
                "type": "string",
                "metadata": {
                    "description": "Size of the data volume in gigabytes.",
                }
            }
        }

    def get_variables(self):
        """ get_variables returns a dict cotaining the variable
        which will be storing the volume's URI on Azure.
        """
        return {
            "diskUri_%s" % self._name:
                "[concat('http://',parameters('newStorageAccountName'),"
                "'.blob.core.windows.net/',"
                "variables('vmStorageAccountContainerName'),"
                "'/%s.vhd')]" % self._name,
        }
