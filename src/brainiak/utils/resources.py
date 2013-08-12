# -*- coding: utf-8 -*-
import re
from tornado.web import HTTPError
from brainiak.prefixes import expand_uri, is_compressed_uri, ROOT_CONTEXT
from brainiak.utils.links import pagination_items
from brainiak.settings import EVENT_BUS_PORT


class LazyObject(object):
    def __init__(self, factory):
        self.factory = factory

    def __getattr__(self, item):
        obj = self.factory()
        return object.__getattribute__(obj, item)


def check_messages_when_port_is_mentioned(source_message):
    backends = {EVENT_BUS_PORT: 'ActiveMQ'}
    port_pattern = re.compile('(\d+)')
    result = []
    for i in port_pattern.findall(source_message):
        port = int(i)
        if port in backends:
            result.append(" Check {0}".format(backends[port]))
    return result


def decorate_dict_with_pagination(target_dict, params, get_total_items_func):
    if params.get("do_item_count", None) == "1":
        total_items = get_total_items_func()
        validate_pagination_or_raise_404(params, total_items)
        target_dict['item_count'] = total_items
        target_dict['do_item_count'] = "1"
    else:
        total_items = None
        target_dict['do_item_count'] = "0"

    target_dict.update(pagination_items(params, total_items))


def valid_pagination(total, page, per_page):
    "Verify if the given pagination is valid to the existent total items"
    return (page * per_page) < total


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
            dict_item['resource_id'] = unicode(resource_id)
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
