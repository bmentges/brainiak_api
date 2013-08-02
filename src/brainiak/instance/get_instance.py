# -*- coding: utf-8 -*-

from brainiak import triplestore, settings
from brainiak.utils.links import build_class_url
from brainiak.prefixes import MemorizeContext
from brainiak.utils.sparql import get_super_properties, is_result_empty


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
    super_predicates = get_super_properties(context, bindings)

    items_dict = {}
    for item in bindings:
        predicate_uri = context.normalize_uri_key(item["predicate"]["value"])
        value = context.normalize_uri_value(item["object"]["value"])
        if predicate_uri in items_dict:
            if not isinstance(items_dict[predicate_uri], list):
                value_list = [items_dict[predicate_uri]]
            else:
                value_list = items_dict[predicate_uri]
            value_list.append(value)
            items_dict[predicate_uri] = value_list
        else:
            items_dict[predicate_uri] = value

    remove_super_properties(context, items_dict, super_predicates)

    if not class_uri is None:
        items_dict[context.normalize_uri_key("rdf:type")] = context.normalize_uri_value(class_uri)

    return items_dict


def remove_super_properties(context, items_dict, super_predicates):
    for (analyzed_predicate, value) in items_dict.items():
        if analyzed_predicate in super_predicates.keys():
            sub_predicate = super_predicates[analyzed_predicate]
            sub_value = items_dict[context.normalize_uri_key(sub_predicate)]
            if value == sub_value or (sub_value in value):
                items_dict.pop(analyzed_predicate)


def assemble_instance_json(query_params, query_result_dict, context=None):
    if context is None:
        context = MemorizeContext(normalize_keys=query_params['expand_uri_keys'],
                                  normalize_values=query_params['expand_uri_values'])

    items = build_items_dict(context, query_result_dict['results']['bindings'], query_params["class_uri"])
    class_url = build_class_url(query_params)
    query_params.resource_url = "{0}/{1}".format(class_url, query_params['instance_id'])

    instance = {
        "_base_url": query_params.base_url,
        "_resource_id": query_params['instance_id'],
        "@id": query_params['instance_uri'],
        "@type": context.normalize_uri_value(query_params["class_uri"]),
        "@context": context.context,
    }
    instance.update(items)
    return instance


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = """
DEFINE input:inference <%(ruleset)s>
SELECT DISTINCT ?predicate ?object ?super_property {
    <%(instance_uri)s> a <%(class_uri)s>;
        ?predicate ?object .
OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
FILTER((langMatches(lang(?object), "%(lang)s") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
}
"""


def query_all_properties_and_objects(query_params):
    query_params["ruleset"] = settings.DEFAULT_RULESET_URI
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % query_params
    return triplestore.query_sparql(query)
