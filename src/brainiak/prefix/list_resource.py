from brainiak.prefixes import get_prefixes_dict, ROOT_CONTEXT


def list_prefixes():
    prefixes_dict = get_prefixes_dict()
    result_dict = dict([("@context", prefixes_dict), ("root_context", ROOT_CONTEXT)])

    return result_dict
