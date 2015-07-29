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
    Definitions of various Azure-related constants.
"""

ARM_API_2015_05_01_PREVIEW = "2015-05-01-preview"
ARM_SCHEMA_URL_2015_01_01 = ("https://schema.management.azure.com/schemas/"
                             "2015-01-01/deploymentTemplate.json#")

# the version of the API to be used in all definitions:
ARM_API_VERSION = ARM_API_2015_05_01_PREVIEW

# ARM_SCHEMA_URL is the default URL for fetching the ARM template JSON schema:
ARM_SCHEMA_URL = ARM_SCHEMA_URL_2015_01_01

# ARM_TEMPLATE_VERSION is the version the resulting template will be on:
ARM_TEMPLATE_VERSION = "1.0.0.0"

# DEFAULT_STORAGE_ACCOUNT_TYPE is the default type for the storage account to
# be created for the deployment if required.
DEFAULT_STORAGE_ACCOUNT_TYPE = "Standard_LRS"

# DEFAULT_STORAGE_CONTAINER_NAME is the default name for the
# storage container to be used.
DEFAULT_STORAGE_CONTAINER_NAME = "vhds"

# DEFAULT_LOCATION is the default location to be used for the deployment.
DEFAULT_LOCATION = "West US"
