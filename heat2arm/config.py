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
    This module contains the definition of various configuration file options
    in the main config class.
"""

from oslo_config import cfg


CONF = cfg.CONF
CONF.register_opts([
    cfg.StrOpt(
        'azure_location',
        default="West US",
        help='The location to be used for the deployment.'
    ),
    cfg.StrOpt(
        'azure_storage_account_type',
        default="Standard_LRS",
        choices=[
            "Standard_LRS",
            "Standard_ZRS",
            "Standard_GRS",
            "Standard_RAGRS",
            "Premium_LRS"
        ],
        help='The type of storage account to be used for the deployment.'
    ),
    cfg.StrOpt(
        'azure_storage_container_name',
        default='vhds',
        help='The name of the storage container to be used for the deployment.'
    ),
    cfg.BoolOpt(
        'validate_arm_template_data',
        default=False,
        help='Flag on whether or not to perform schema validation on the'
             'resulting template.'
    ),
    cfg.StrOpt(
        'arm_api_version',
        default="2015-05-01-preview",
        help='The ARM API version resources should be defined against.'
    ),
    cfg.StrOpt(
        'arm_schema_url',
        default="https://schema.management.azure.com/schemas/"
                "2015-01-01/deploymentTemplate.json#",
        help="URL of the schema to be used when validating the resulting"
             "template. Also used within the template itself."
    ),
    cfg.StrOpt(
        'arm_template_version',
        default="1.0.0.0",
        help="The version to be stamped onto the resulting ARM template."
    ),
    cfg.DictOpt(
        "ec2_flavor_to_size_map",
        default={
            "m1.tiny": "Basic_A0",
            "m1.small": "Basic_A1",
            "m1.medium": "Basic_A2",
            "m1.large": "Basic_A3",
            "m1.xlarge": "basic_A4",
        },
        help="A mapping between EC2 Instance flavors and Azure machine sizes."
    ),
    cfg.DictOpt(
        "ec2_vm_image_map",
        default={
            "U10-x86_64-cfntools":
            "Canonical;UbuntuServer;12.04.5-LTS",
            "F17-x86_64-cfntools":
            "Canonical;UbuntuServer;12.04.5-LTS"
        },
        help="A map between EC2 image names and Azure ones.",
    ),
    cfg.DictOpt(
        'nova_flavor_to_size_map',
        default={
            'm1.tiny': "Basic_A0",
            'm1.small': "Basic_A1",
            'm1.medium': "Basic_A2",
            'm1.large': "Basic_A3",
            'm1.xlarge': "Basic_A4",
        },
        help='A mapping between OpenStack Nova flavors and Azure VM sizes.'
    ),
    cfg.DictOpt(
        'nova_vm_image_map',
        default={
            'ubuntu.12.04.LTS.x86_64':
            "Canonical;UbuntuServer;12.04.5-LTS",
        },
        help='A mapping between OpenStack Nova and Azure VM images'
    ),
    # ####################### AutoScaling translation parameters:
    cfg.StrOpt(
        'arm_autoscale_settings_api_version',
        default="2014-04-01",
        help='The ARM API version to be used when declaring autoscaleSettings,'
             ' as they require an older API version than any other resource.'
    ),
    cfg.FloatOpt(
        'autoscaling_min_cpu_threshold',
        default=60.0,
        help="The lower bound of CPU load percentage after which scale downs "
             "should insue."
    ),
    cfg.IntOpt(
        'arm_fault_domain_count',
        default=2,
        help="The number of replicas to be created representing the "
             "availabilitySet's fault domain."
    ),
    cfg.FloatOpt(
        'autoscaling_max_cpu_threshold',
        default=80.0,
        help="The upper bound of CPU load percentage after which scale ups "
             "should insue."
    ),
    cfg.ListOpt(
        'default_autoscaleSettings_rules',
        default=[{
            "metricTrigger": {
                "metricName": "CpuPercentage",
                "timeGrain": "PT1M",
                "statistic": "Average",
                "timeWindow": "PT10M",
                "timeAggregation": "Average",
                "operator": "GreaterThan",
                "threshold": 80.0
            },
            "scaleAction": {
                "direction": "Increase",
                "type": "ChangeCount",
                "value": "1",
                "cooldown": "PT10M"
            }
        }, {
            "metricTrigger": {
                "metricName": "CpuPercentage",
                "timeGrain": "PT1M",
                "statistic": "Average",
                "timeWindow": "PT1H",
                "timeAggregation": "Average",
                "operator": "LessThan",
                "threshold": 60.0
            },
            "scaleAction": {
                "direction": "Decrease",
                "type": "ChangeCount",
                "value": "1",
                "cooldown": "PT1H"
            }
        }]
    )
])
