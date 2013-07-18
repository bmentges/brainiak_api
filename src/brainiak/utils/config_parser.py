from ConfigParser import ConfigParser, NoSectionError


def parse_section(filename, section="default"):
    parser = ConfigParser()
    parser.read(filename)
    try:
        config_dict = dict(parser.items('default'))
    except NoSectionError:
        raise Exception("There is no {0} section in the file {1}".format(section, filename))
    return config_dict
