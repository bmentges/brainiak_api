from ConfigParser import ConfigParser, NoSectionError


def parse_section(filename, section="default"):
    try:
        parser = ConfigParser()
        parser.read(filename)
        keys = parser.options(section)
    except NoSectionError:
        raise RuntimeError("There is no {0} section in the file".format(section))
    config_dict = {}
    for key in keys:
        value = parser.get(section, key)
        config_dict[key] = value
    return config_dict
