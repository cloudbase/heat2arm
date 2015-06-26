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

import argparse
import json
import logging
import os
import sys
import warnings

from oslo_config import cfg
import yaml

from heat2arm import translation_engine as engine

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def _open_file_read(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'rb')


def _open_file_write(parser, arg):
    return open(arg, 'wb')


def _parse_args():
    parser = argparse.ArgumentParser(
        description='OpenStack Heat to Azure ARM template converter.')
    parser.add_argument("--in", dest="heat_template", required=True,
                        help="Path to the OpenStack Heat template to convert",
                        type=lambda x: _open_file_read(parser, x))
    parser.add_argument("--out", dest="arm_template",
                        help="Optional Azure ARM template output path",
                        type=lambda x: _open_file_write(parser, x),
                        default=sys.stdout)
    parser.add_argument("--config-file",
                        help="Path to an optional configuration file",
                        type=str)
    return parser.parse_args()


def _setup_logging():
    streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
    logging.basicConfig(level=logging.WARNING,
                        format=streamformat)
    # Disable Heat warnings
    warnings.simplefilter("ignore")


def main():
    _setup_logging()

    args = _parse_args()
    if args.config_file:
        CONF(["--config-file", args.config_file])

    heat_template_data = yaml.load(args.heat_template, Loader=yaml.BaseLoader)
    args.heat_template.close()

    arm_template_data = engine.convert_template(heat_template_data)

    args.arm_template.write(json.dumps(arm_template_data, indent=4))
    args.arm_template.close()

if __name__ == "__main__":
    main()
