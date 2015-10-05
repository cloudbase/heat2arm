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
    This file contains constants used for the translation of AutoScalingGroups.
"""

# SCALING_MIN_THRESHOLD and SCALING_MAX_THRESHOLD are the two thresholds
# to be used when setting scale down and up conditions respectively:
SCALING_MIN_THRESHOLD = 60.0
SCALING_MAX_THRESHOLD = 80.0

# ADJUSTMENT_TYPE_TO_SCALE_TYPE_MAP is a mapping between the adjustment types
# of AWS ScalingPolicies and the scale types of Azure autoscaleSettings rules.
ADJUSTMENT_TYPE_TO_SCALE_TYPE_MAP = {
    "ChangeInCapacity": "ChangeCount",
    "ExactCapacity": "ChangeCount",
    "PercentChangeInCapacity": "PercentChangeCount"
}

# DEFAULT_AUTOSCALESETTINGS_RULES is the default rules to be applied for
# autoscaleSettings on Azure if no AWS ScalingPolicy was provided for
# the AutoScalingGroup being translated:
DEFAULT_AUTOSCALESETTINGS_RULES = [
    {
        "metricTrigger": {
            "metricName": "CpuPercentage",
            "timeGrain": "PT1M",
            "statistic": "Average",
            "timeWindow": "PT10M",
            "timeAggregation": "Average",
            "operator": "GreaterThan",
            "threshold": SCALING_MAX_THRESHOLD
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
            "threshold": SCALING_MIN_THRESHOLD
        },
        "scaleAction": {
            "direction": "Decrease",
            "type": "ChangeCount",
            "value": "1",
            "cooldown": "PT1H"
        }
    }
]
