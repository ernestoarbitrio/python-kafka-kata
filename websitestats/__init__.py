# coding: utf-8

"""Parser for settings.ini"""

import os
from configparser import ConfigParser, ExtendedInterpolation

PRJ_DIR = os.path.dirname(os.path.realpath(__file__))


class ExtendedEnvInterpolation(ExtendedInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        return os.path.expandvars(value)


def config(section, filename=os.path.join(PRJ_DIR, "settings.ini")):
    """Parser function for settings."""
    parser = ConfigParser(interpolation=ExtendedEnvInterpolation())
    parser.read(filename)

    service = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            service[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )
    return service
