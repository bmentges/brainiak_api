# coding: utf-8
import re
import uuid


def create_instance_uri(class_uri):
    """
    Create an unique uri for an instance of the class provided.
    """
    return "%s/%s" % (class_uri, uuid.uuid4())


def get_one_value(result_dict, key):
    """
    Return first value mapped by 'key' inside the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}]}}
    >>> get_one_value(result_dict, 'key')
    "some value"
    >>> get_one_value(result_dict, 'inexistent_key')
    False
    """
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def filter_values(result_dict, key):
    """
    Return a list of values mapped by 'key' inside the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}, {'key': {'type': 'some type', 'value': 'another value'}}]}}
    >>> filter_values(result_dict, 'key')
    ["some value", "another value"]
    >>> filter_values(result_dict, 'inexistent_key')
    []
    """
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def compress_keys_and_values(result_dict, keymap={}, ignore_keys=[], context=None):
    """
    Return a list of compacted items of the 'bindings' list of a Virtuoso response dict.

    Usage:

    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'some type', 'value': 'some value'}}, {'key': {'type': 'some type', 'value': 'another value'}}]}}
    >>> compress_keys_and_values(result_dict)
    [{'key': 'some value'}, {'key': 'another value'}]

    Optional params:

    - keymap = {'key': 'renamed_key'}: renames resulting dict 'key' by 'renamed_key'
    - ignore_keys = ['key']: list of keys that shouldn't be returned
    - context (instance of MemorizeContext): shortens URIs according to provided context

    >>> compress_keys_and_values(result_dict, keymap={'key': 'renamed_key'})
    [{'renamed_key': 'some value'}, {'renamed_key': 'another value'}]

    >>> compress_keys_and_values(result_dict, ignore_keys=['key'])
    []

    >>> from brainiak.prefixes import MemorizeContext
    >>> result_dict = {'results': {'bindings': [{'key': {'type': 'uri', 'value': 'http://xmlns.com/foaf/0.1/value'}}]}}
    >>> context = MemorizeContext()
    >>> compress_keys_and_values(result_dict, context=context)
    [{'key': 'foaf:value'}]

    """
    result_list = []
    for item in result_dict['results']['bindings']:
        row = {}
        for key in item:
            if not key in ignore_keys:
                value = item[key]['value']
                if item[key]['type'] == 'uri' and context:
                    value = context.shorten_uri(value)
                row[keymap.get(key, key)] = value
        result_list.append(row)
    return result_list


def is_result_empty(result_dict):
    """
    Return True if result_dict['results']['bindings'] has no items, False otherwise.
    """
    return not result_dict['results']['bindings']


def some_triples_deleted(result_dict, graph_uri):
    """
    Return True if result_dict['results']['bindings'][0]['callret-0']['value'] has a message like
    "Delete from <a>, 1 (or less) triples -- done"

    If the message is like "Delete from <a>, 0 triples -- nothing to do" False is returned

    If no patterns matched, raise an Exception, probably Virtuoso message changed

    >>> result_dict = { "head": { "link": [], "vars": ["callret-0"] }, "results": { "distinct": false, "ordered": true, "bindings": [{ "callret-0": { "type": "literal", "value": "Delete from <a>, 1 (or less) triples -- done" }} ] } }
    >>> zero_triples_deleted(result_dict)
    >>> True

    """
    try:
        query_result_message = result_dict['results']['bindings'][0]['callret-0']['value']
    except:
        raise UnexpectedResultException("Unknown result format: " + str(result_dict))
    delete_successful_message = "Delete from <%s>, ([0-9]*) \(or less\) triples -- done" % graph_uri
    not_found_message = "Delete from <%s>, 0 triples -- nothing to do" % graph_uri

    if re.search(delete_successful_message, query_result_message):
        return True
    elif re.search(not_found_message, query_result_message):
        return False
    else:
        raise UnexpectedResultException("Unknown result format: " + str(result_dict))


class UnexpectedResultException(Exception):
    pass
