# -*- coding: utf-8 -*-
from copy import copy

from brainiak import triplestore
from brainiak.prefixes import MemorizeContext, shorten_uri
from brainiak.utils.links import assemble_url, build_class_url, build_schema_url, self_link, crud_links, add_link, filter_query_string_by_key_prefix, remove_last_slash
from brainiak.utils.sparql import expand_uri, get_super_properties, is_result_empty


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


def build_items_dict(context, bindings, class_uri):
    super_predicates = get_super_properties(bindings)

    items_dict = {}
    for item in bindings:
        predicate_uri = context.shorten_uri(item["predicate"]["value"])
        value = context.shorten_uri(item["object"]["value"])
        if predicate_uri in items_dict:
            if not isinstance(items_dict[predicate_uri], list):
                value_list = [items_dict[predicate_uri]]
            else:
                value_list = items_dict[predicate_uri]
            value_list.append(value)
            items_dict[predicate_uri] = value_list
        else:
            items_dict[predicate_uri] = value

    # remove super properties that have the same value as subproperties
    for (analyzed_predicate, value) in items_dict.items():
        if analyzed_predicate in super_predicates.keys():
            sub_predicate = super_predicates[analyzed_predicate]
            sub_value = items_dict[sub_predicate]
            if value == sub_value:
                items_dict.pop(analyzed_predicate)

    if not class_uri is None:
        items_dict["rdf:type"] = context.shorten_uri(class_uri)

    # overwrite label only with filtered language
    if expand_uri("rdfs:label") not in super_predicates:
        items_dict["rdfs:label"] = item["label"]["value"]
    else:
        items_dict.pop("rdfs:label")

    return items_dict


def assemble_instance_json(query_params, query_result_dict, context=None):
    if context is None:
        context = MemorizeContext()

    items = build_items_dict(context, query_result_dict['results']['bindings'], query_params["class_uri"])
    links = [{"rel": property_name,
             "href": "/{0}/{1}".format(*(uri.split(':')))}
             for property_name, uri in context.object_properties.items()]

    class_url = build_class_url(query_params)
    class_url_with_query_string = build_class_url(query_params, include_query_string=True)
    schema_url = build_schema_url(query_params)

    query_params.resource_url = "{0}/{1}".format(class_url, query_params['instance_id'])
    action_links = self_link(query_params) + crud_links(query_params)
    add_link(links, 'describedBy', schema_url)
    add_link(links, 'inCollection', class_url_with_query_string)

    links.extend(action_links)

    instance = {
        "@id": query_params['instance_uri'],
        "@type": shorten_uri(query_params["class_uri"]),
        "@context": context.context,
        "links": links,
    }
    instance.update(items)
    return instance


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = """
DEFINE input:inference <%(ruleset)s>
SELECT DISTINCT ?predicate ?object ?label ?super_property {
    <%(instance_uri)s> a <%(class_uri)s>;
        rdfs:label ?label;
        ?predicate ?object .
OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
FILTER(langMatches(lang(?label), "%(lang)s") OR langMatches(lang(?label), "")) .
}
"""


def query_all_properties_and_objects(query_params):
    query_params["ruleset"] = "http://semantica.globo.com/ruleset"
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % query_params
    return triplestore.query_sparql(query)
