# -*- coding: utf-8 -*-
from brainiak import triplestore
from brainiak.prefixes import MemorizeContext
from brainiak.utils.links import self_link, crud_links, add_link, remove_last_slash
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

    items = build_items_dict(context, query_result_dict['results']['bindings'])
    links = [{"rel": property_name,
             "href": "/{0}/{1}".format(*(uri.split(':')))}
             for property_name, uri in context.object_properties.items()]

    base_url = "{0}://{1}/{2}/{3}".format(
        query_params['request'].protocol,
        query_params['request'].host,
        query_params['context_name'],
        query_params['class_name'])
    href_schema_url = "{0}/_schema".format(base_url)
    query_params.resource_url = "{0}/{1}".format(base_url, query_params['instance_id'])
    action_links = self_link(query_params) + crud_links(query_params)
    add_link(links, 'describedBy', href_schema_url)
    add_link(links, 'inCollection', base_url)

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
