# -*- coding: utf-8 -*-


def decorate_with_resource_id(list_of_dicts):
    """Adds to each entry in the input parameter list_of_dicts
    a new key`resource_id` created from the last path segment given by the key `@id`"""
    for dict_item in list_of_dicts:
        try:
            id_key = dict_item["@id"]
            dict_item['resource_id'] = id_key.rsplit("/")[-1]
        except KeyError:
            pass
