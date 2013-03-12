# -*- coding: utf-8 -*-
import json
from tornado import gen

from brainiak import triplestore
from brainiak.prefixes import expand_uri, MemorizeContext
from brainiak.result_handler import compress_keys_and_values, is_result_empty, convert_bindings_dict
from brainiak.settings import URI_PREFIX


def get_instance(request, context_name, class_name, instance_id):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    query_response = query_all_properties_and_objects(context_name, class_name, instance_id)
    query_result_dict = json.loads(query_response.body)

    if is_result_empty(query_result_dict):
        return
    else:
        # TODO handling dict
        return assemble_instance_json(request, context_name, class_name, query_result_dict)


def assemble_instance_json(request, context_name, class_name, query_result_dict):
    context = MemorizeContext()
    base_url = request.headers.get("Host")
    #predicates = convert_bindings_dict(context, query_result_dict['results']['bindings'], None)
    links = [{"rel": property_name,
             "href": "/{0}/{1}".format(*(uri.split(':')))}
              for property_name, uri in context.object_properties.items()]

    instance = {
        "type": "object",
        "@id": request.full_url(),
        "@context": context.context,
        "$schema": "http://{0}/{1}/{2}/_schema".format(base_url, context_name, class_name),
        #"title": title,
        "links": links,
        #"properties": predicates
    }
    return instance


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = """
SELECT ?p ?o {
<%(prefix)s%(context_name)s/%(class_name)s/%(instance_id)s> a <%(prefix)s%(context_name)s/%(class_name)s>;
    ?p ?o}
"""


def query_all_properties_and_objects(context_name, class_name, instance_id):
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % {
        'instance_id': instance_id,
        'prefix': URI_PREFIX,
        'context_name': context_name,
        'class_name': class_name,
    }

    return triplestore.query_sparql(query)


QUERY_FILTER_INSTANCE = """
SELECT DISTINCT ?subject ?label
FROM <%(graph_uri)s>
WHERE {
    ?subject a <%(class_uri)s>;
             rdfs:label ?label;
             %(p)s %(o)s .
    %(lang_filter)s
}
ORDER BY ASC (xsd:string(?label))
LIMIT %(per_page)s
OFFSET %(page)s
"""


QUERY_FILTER_LABEL_BY_LANGUAGE = """
    FILTER(langMatches(lang(?label), "%(lang)s")) .
"""


def lang_support(lang):
    if lang:
        return "@%s" % lang
    else:
        return ""


def query_filter_instances(query_params):
    """
    Important note: when "lang" is defined in query_params,
    the languge provided:
        - is applied to ALL literals of the query
        - labels will be filtered according to <lang>
    """
    potential_uris = ["o", "p"]
    language_tag = lang_support(query_params.get("lang"))

    for key in potential_uris:
        value = query_params[key]
        if (not value.startswith("?")):
            if (":" in value):
                query_params[key] = "<%s>" % expand_uri(value)
            else:
                query_params[key] = '"%s"%s' % (value, language_tag)

    if language_tag:
        query_params["lang_filter"] = QUERY_FILTER_LABEL_BY_LANGUAGE % query_params
    else:
        query_params["lang_filter"] = ""

    query = QUERY_FILTER_INSTANCE % query_params

    return triplestore.query_sparql(query)


def filter_instances(query_params):
    query_response = query_filter_instances(query_params)
    result_dict = json.loads(query_response.body)

    if is_result_empty(result_dict):
        return None
    else:
        items_list = compress_keys_and_values(result_dict)
        return {'items': items_list, 'item_count': len(items_list)}
