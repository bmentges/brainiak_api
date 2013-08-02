from brainiak import settings
from ConfigParser import ConfigParser, NoSectionError


class ConfigParserNoSectionError(Exception):
    pass


def parse_section(filename=settings.TRIPLESTORE_CONFIG_FILEPATH, section="default"):
    parser = ConfigParser()
    parser.read(filename)
    try:
        config_dict = dict(parser.items(section))
    except NoSectionError:
        raise ConfigParserNoSectionError("There is no {0} section in the file {1}".format(section, filename))
    return config_dict
