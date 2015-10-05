"""
    This module provides a baseline implementation for a Heat template parser.

    The template may be provided in either YAML or JSON format.

        Usage example:

    >>> from heat2arm.parser.parser import parse_file
    >>>
    >>> resources = parse_file('/path/to/heat_template.yaml')
    >>> for res in resources:
    ...     print res.properties
    >>>
"""
