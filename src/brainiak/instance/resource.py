# -*- coding: utf-8 -*-
import json
from tornado import gen

from brainiak.prefixes import expand_uri
from brainiak.result_handler import compress_keys_and_values, is_result_empty
from brainiak.settings import URI_PREFIX
from brainiak.triplestore import query_sparql


@gen.engine
def get_instance(context_name, class_name, instance_id, callback):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    query_response = yield gen.Task(query_all_properties_and_objects, context_name, class_name, instance_id)
    result_dict = json.loads(query_response.body)

    if is_result_empty(result_dict):
        callback(None)
    else:
        # TODO handling dict
        callback(result_dict)


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = """
SELECT ?p ?o {
<%(prefix)s/%(context_name)s/%(class_name)s/%(instance_id)s> a <%(prefix)s/%(context_name)s/%(class_name)s>;
    ?p ?o}
"""


def query_all_properties_and_objects(context_name, class_name, instance_id, callback):
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % {
        'instance_id': instance_id,
        'prefix': URI_PREFIX,
        'context_name': context_name,
        'class_name': class_name,
    }
    query_sparql(callback, query)


QUERY_FILTER_INSTANCE = """
SELECT DISTINCT ?subject, ?label {
    ?subject a <%(class_uri)s>;
             rdfs:label ?label;
             %(predicate)s %(object)s .
}
"""


def query_filter_instances(context_name, query_params, callback):
    potential_uris = ["object", "predicate"]

    for key in potential_uris:
        value = query_params[key]
        if (not value.startswith("?")):
            if (":" in value):
                query_params[key] = "<%s>" % expand_uri(value)
            else:
                query_params[key] = '"%s"@pt' % value

    query = QUERY_FILTER_INSTANCE % query_params
    query_sparql(callback, query)


@gen.engine
def filter_instances(context_name, query_params, callback):
    query_response = yield gen.Task(query_filter_instances, context_name, query_params)
    result_dict = json.loads(query_response.body)

    if is_result_empty(result_dict):
        callback({'items': [], 'item_count': 0})
    else:
        items_list = compress_keys_and_values(result_dict)
        callback({'items': items_list, 'item_count': len(items_list)})
