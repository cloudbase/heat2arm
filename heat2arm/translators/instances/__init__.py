"""
    This module contains definitions for both the Nova and
    Cloud Formation instance translators.
"""

from heat2arm.translators.instances.ec2_instance import (
    EC2InstanceARMTranslator
)
from heat2arm.translators.instances.nova_server import NovaServerARMTranslator
