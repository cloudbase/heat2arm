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

ARM_API_2014_04_01 = "2014-04-01"


# EC2_TO_ARM_SIZE_MAPPINGS is the set of mappings between EC2 VM sizes
# and Azure instance sizes.
EC2_TO_ARM_SIZE_MAPPINGS = {
    "m1.tiny": "Basic_A0",
    "m1.small": "Basic_A1",
    "m1.medium": "Basic_A2",
    "m1.large": "Basic_A3",
    "m1.xlarge": "basic_A4",
}

# EC2_TO_ARM_IMAGE_MAPPINGS is the set of mappings between EC2 VM images
# and deployable Azure images.
EC2_TO_ARM_IMAGE_MAPPINGS = {
    "U10-x86_64-cfntools":  "Canonical;UbuntuServer;12.04.5-LTS",
    "F17-x86_64-cfntools":  "Canonical;UbuntuServer;12.04.5-LTS"
}

# NOVA_TO_ARM_SIZE_MAPPINGS is the set of mappings between Nova VM sizes
# and Azure instance sizes.
NOVA_TO_ARM_SIZE_MAPPINGS = {
    'm1.tiny': "Basic_A0",
    'm1.small': "Basic_A1",
    'm1.medium': "Basic_A2",
    'm1.large': "Basic_A3",
    'm1.xlarge': "Basic_A4",
}

# NOVA_TO_ARM_IMAGE_MAPPINGS is the set of mappings between Nova VM
# images and deployable Azure images.
NOVA_TO_ARM_IMAGE_MAPPINGS = {
    'ubuntu.12.04.LTS.x86_64':  "Canonical;UbuntuServer;12.04.5-LTS",
}

# VM_DEFAULT_SIZE is the default size of an instance on Azure.
VM_DEFAULT_SIZE = "Basic_A1"

# VALIDATE_TEMPLATE_SCHEMA denotes whether the resulting template
# should be validated agains the latest ARM schema.
VALIDATE_TEMPLATE_SCHEMA = False
