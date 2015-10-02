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
    Main entry point of the application.
"""

import argparse
import json
import sys

from heat2arm.config import CONF

from heat2arm import translation_engine as engine


def _parse_args():
    """ _parse_args is a helper function which sets up command line
    arguments and returns the argument parser object.
    """
    parser = argparse.ArgumentParser(
        description='OpenStack Heat to Azure ARM template converter.')
    parser.add_argument("--in", dest="heat_template", required=True,
                        help="Path to the OpenStack Heat template to convert",
                        type=argparse.FileType('rb'))
    parser.add_argument("--out", dest="arm_template",
                        help="Optional Azure ARM template output path",
                        type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument("--config-file",
                        help="Path to an optional configuration file",
                        type=str)
    return parser.parse_args()


def main():
    """ main is the entry point of the application. """
    args = _parse_args()

    if args.config_file:
        CONF(["--config-file", args.config_file])

    heat_template_data = args.heat_template.read()
    args.heat_template.close()

    arm_template_data = engine.convert_template(heat_template_data)

    args.arm_template.write(json.dumps(arm_template_data, indent=4))
    args.arm_template.close()


if __name__ == "__main__":
    main()
