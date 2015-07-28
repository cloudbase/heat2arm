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
    This package contains some "global" variables used to sync certain
    sub-modules of the project.
"""

# NEW_STORAGE_ACC_REQUIRED specifies whether a new storage account should be
# created in order to support the storage-related tasks of the deployment.
NEW_STORAGE_ACC_REQUIRED = False

# NEW_VIRTUAL_NETWORK_REQUIRED specifies whether a new default virtual network
# is required to be created to support the deployment.
NEW_VIRTUAL_NETWORK_REQUIRED = False

# AVAILABILITY_SET_NAMES is a list of the names of availability sets registered
# so far to exist. It is necessary due to the fact that it is mostly the
# translator's jobs to add new ones if necessary.
AVAILABILITY_SET_NAMES = []
