# -*- coding: utf-8 -*-
from brainiak import triplestore
from brainiak.prefixes import MemorizeContext
from brainiak.utils.sparql import is_result_empty


def get_instance(query_params):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    query_result_dict = query_all_properties_and_objects(query_params)

    if is_result_empty(query_result_dict):
        return None
    else:
        return assemble_instance_json(query_params,
                                      query_result_dict)


def build_items_dict(context, bindings):
    items_dict = {}
    for item in bindings:
        key = context.shorten_uri(item["p"]["value"])
        value = context.shorten_uri(item["o"]["value"])
        if key in items_dict:
            if not isinstance(items_dict[key], list):
                value_list = [items_dict[key]]
            else:
                value_list = items_dict[key]
            value_list.append(value)
            items_dict[key] = value_list
        else:
            items_dict[key] = value
    return items_dict


def assemble_instance_json(query_params, query_result_dict, context=None):
    if context is None:
        context = MemorizeContext()
    request = query_params['request']
    base_url = request.headers.get("Host")
    items = build_items_dict(context, query_result_dict['results']['bindings'])
    links = [{"rel": property_name,
             "href": "/{0}/{1}".format(*(uri.split(':')))}
             for property_name, uri in context.object_properties.items()]

    self_url = request.full_url()
    schema_url = "http://{0}/{1}/{2}/_schema".format(base_url, query_params['context_name'], query_params['class_name'])

    action_links = [
        {'rel': 'self', 'href': self_url},
        {'rel': 'describedBy', 'href': schema_url},
        {'rel': 'replace', 'method': 'PUT', 'href': self_url},
        {'rel': 'delete', 'method': 'DELETE', 'href': self_url}
    ]
    links.extend(action_links)

    instance = {
        "@id": query_params['instance_uri'],
        "@type": "{0}:{1}".format(query_params['context_name'], query_params['class_name']),
        "@context": context.context,
        "links": links,
    }
    instance.update(items)
    return instance


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = """
SELECT ?p ?o {
<%(instance_uri)s> a <%(class_uri)s>;
    ?p ?o}
"""


def query_all_properties_and_objects(query_params):
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % query_params
    return triplestore.query_sparql(query)
