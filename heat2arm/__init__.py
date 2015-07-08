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
