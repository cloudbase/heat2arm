"""
    Command line tool which translates Heat templates (be them in clasic YAML
    or Cloud Formation format) into ARM templates.

        Usage example:

    >>> from heat2arm.translation_engine import convert_template
    >>>
    >>> with open('heat_template.yaml') as f:
    ...     heat_template = f.read()
    ...     arm_template = convert_template(heat_template)
    ...     print arm_template
    >>>


        Install guide:

    # python setup.py install
    $ heat2arm --in heat_template.yaml --out arm_template.json
"""

import logging
import sys


LOGGER = logging.getLogger("__heat2arm__")
STDOUTSH = logging.StreamHandler(sys.stderr)
STDOUTSH.setFormatter(logging.Formatter("%(asctime)s - %(name)s -"
                                        "%(levelname)s - %(message)s"))
STDOUTSH.setLevel(logging.DEBUG)
LOGGER.addHandler(STDOUTSH)
