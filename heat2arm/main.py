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
import logging
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
    parser.add_argument("--loglevel",
                        help="The logging level to be used.",
                        default="WARNING",
                        type=str)
    parser.add_argument("--logfile",
                        help="The file to be used for logging.",
                        type=argparse.FileType('w'),
                        default=sys.stderr)
    return parser.parse_args()


def _setup_logging(file, level):
    """ _setup_logging is a helper method which sets up the logging
    process to the given file and with the given level (as a string).
    """
    log_level = getattr(logging, level.upper(), None)
    if not log_level:
        raise Exception("Invalid log level '%s' provided.")

    logger = logging.getLogger("__heat2arm__")
    logger.setLevel(log_level)
    stdoutsh = logging.StreamHandler(file)
    stdoutsh.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(stdoutsh)


def main():
    """ main is the entry point of the application. """
    args = _parse_args()

    # first; check for a config file and load it:
    if args.config_file:
        CONF(["--config-file", args.config_file])

    # setup logging:
    _setup_logging(args.logfile, args.loglevel)

    # read the contents of the template:
    heat_template_data = args.heat_template.read()
    args.heat_template.close()

    # do the conversion:
    arm_template_data = engine.convert_template(heat_template_data)

    # write out the result:
    args.arm_template.write(json.dumps(arm_template_data, indent=4))
    args.arm_template.close()


if __name__ == "__main__":
    main()
