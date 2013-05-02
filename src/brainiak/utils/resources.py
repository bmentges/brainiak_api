# -*- coding: utf-8 -*-
from tornado.web import HTTPError
from brainiak.prefixes import expand_uri, is_compressed_uri, ROOT_CONTEXT
from brainiak.utils.params import valid_pagination


def validate_pagination_or_raise_404(params, total_items):
    "Uniform validation for a page out of range"
    page_index = int(params["page"])
    per_page = int(params["per_page"])
    if not valid_pagination(total_items, page_index, per_page):
        raise HTTPError(404, log_message="Page {0:d} not found.".format(page_index + 1))


def decorate_with_resource_id(list_of_dicts):
    """Adds to each entry in the input parameter list_of_dicts
    a new key`resource_id` created from the last path segment given by the key `@id`"""
    for dict_item in list_of_dicts:
        try:
            id_key = expand_uri(dict_item["@id"])
            title = dict_item.get("title")
            if title == ROOT_CONTEXT:
                resource_id = u''
            elif id_key.endswith("/"):
                resource_id = id_key.rsplit("/")[-2]
            else:
                resource_id = id_key.rsplit("/")[-1]
            dict_item['resource_id'] = resource_id
        except KeyError as ex:
            raise TypeError("dict missing key {0:s} while processing decorate_with_resource_id()".format(ex))


def decorate_with_class_prefix(list_of_dicts):
    for dict_item in list_of_dicts:
        uri = dict_item["@id"]
        if is_compressed_uri(uri):
            class_prefix = uri.rsplit(":")[0]
        else:
            pos = uri.rfind("/") + 1
            class_prefix = uri[:pos]
        dict_item["class_prefix"] = class_prefix


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
    except KeyError as ex:
        raise TypeError("dict missing key {0:s} while processing compress_duplicated_ids()".format(ex))
