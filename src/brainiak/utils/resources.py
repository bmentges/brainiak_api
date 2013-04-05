# -*- coding: utf-8 -*-
from brainiak.prefixes import expand_uri


def decorate_with_resource_id(list_of_dicts):
    """Adds to each entry in the input parameter list_of_dicts
    a new key`resource_id` created from the last path segment given by the key `@id`"""
    for dict_item in list_of_dicts:
        try:
            id_key = expand_uri(dict_item["@id"])
            dict_item['resource_id'] = id_key.rsplit("/")[-1]
        except KeyError:
            pass


def compress_duplicated_ids(list_of_dicts):
    """Compress list of dicts with duplicated ids and different argumens values,
    like titles.

    Example:

    >>> resource_dict = [{"@id": "person:Person", "title": "Pessoa"}, {"@id": "person:Person", "title": "Person"}, {"@id": "Person:Gender", "title": "Gender"}]
    >>> compress_duplicated_ids(resource_dict)
    >>> [{"@id": "person:Person", "title": ["Person", "Pessoa"]}, {"@id": "Person:Gender", "title": "Gender"}]
    """
    try:
        ids = list(set(a_dict["@id"] for a_dict in list_of_dicts))
        compressed_list = []
        for id in ids:
            dicts_with_same_id = filter(lambda a_dict: a_dict["@id"] == id, list_of_dicts)
            compressed_dict = dict((key, list(set([d[key] for d in dicts_with_same_id]))) for key in dicts_with_same_id[0])
            # transforming lists with 1 element into a non-list, e.g. a string
            compressed_dict = dict((key, value[0] if len(value) == 1 else value) for key, value in compressed_dict.items())
            compressed_list.append(compressed_dict)
        return compressed_list
    except KeyError:
        pass
