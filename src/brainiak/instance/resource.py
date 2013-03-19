# -*- coding: utf-8 -*-
import json

from brainiak import triplestore
from brainiak.prefixes import expand_uri, MemorizeContext
from brainiak.result_handler import compress_keys_and_values, get_one_value, is_result_empty
from brainiak.settings import URI_PREFIX


def get_instance(query_params):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    query_response = query_all_properties_and_objects(query_params['context_name'],
                                                      query_params['class_name'],
                                                      query_params['instance_id'])
    query_result_dict = json.loads(query_response.body)

    if is_result_empty(query_result_dict):
        return
    else:
        return assemble_instance_json(query_params,
                                      query_result_dict)


def build_items_dict(context, bindings):
    items_dict = {}
    for item in bindings:
        key = context.shorten_uri(item["p"]["value"])
        value = context.shorten_uri(item["o"]["value"])
        items_dict[key] = value
    return items_dict


def assemble_instance_json(query_params, query_result_dict):
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
        {'rel': 'edit', 'method': 'PATCH', 'href': self_url},
        {'rel': 'delete', 'method': 'DELETE', 'href': self_url},
    ]
    links.extend(action_links)

    instance = {
        "@id": self_url,
        "@type": "{0}:{1}".format(query_params['context_name'], query_params['class_name']),
        "@context": context.context,
        "$schema": schema_url,
        "links": links,
    }
    instance.update(items)
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


QUERY_COUNT_FILTER_INSTANCE = """
DEFINE input:inference <http://semantica.globo.com/property_ruleset>
SELECT DISTINCT count (distinct ?subject) as ?total
WHERE {
    ?subject a <%(class_uri)s> ;
             rdfs:label ?label ;
             %(p)s %(o)s.
    %(lang_filter)s
}
"""

QUERY_FILTER_INSTANCE = """
DEFINE input:inference <http://semantica.globo.com/ruleset>
SELECT DISTINCT ?subject ?label
WHERE {
    ?subject a <%(class_uri)s> ;
             rdfs:label ?label ;
             %(p)s %(o)s.
    %(lang_filter)s
}
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


def process_params(query_params):
    """
    Important note: when "lang" is defined in query_params,
    the languge provided:
        - is applied to ALL literals of the query
        - labels will be filtered according to <lang>
    """
    potential_uris = ["o", "p"]
    language_tag = lang_support(query_params.get("lang"))

    for key in potential_uris:
        value = query_params.get(key, "")
        if (not value.startswith("?")):
            if (":" in value):
                query_params[key] = "<%s>" % expand_uri(value)
            else:
                query_params[key] = '"%s"%s' % (value, language_tag)

    if language_tag:
        query_params["lang_filter"] = QUERY_FILTER_LABEL_BY_LANGUAGE % query_params
    else:
        query_params["lang_filter"] = ""

    return query_params


def query_filter_instances(query_params):
    query = QUERY_FILTER_INSTANCE % query_params
    query_response = triplestore.query_sparql(query)
    return query_response


def query_count_filter_intances(query_params):
    query = QUERY_COUNT_FILTER_INSTANCE % query_params
    query_response = triplestore.query_sparql(query)
    return query_response


def filter_instances(query_params):
    query_params = process_params(query_params)
    query_response = query_count_filter_intances(query_params)

    result_dict = json.loads(query_response.body)
    total_items = int(get_one_value(result_dict, 'total'))

    if not total_items:
        return None

    query_response = query_filter_instances(query_params)
    result_dict = json.loads(query_response.body)
    items_list = compress_keys_and_values(result_dict)
    return build_json(items_list, total_items, query_params)


from urlparse import parse_qs
from urllib import urlencode


def set_query_string_parameter(query_string, param_name, param_value):
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    return new_query_string


def build_json(items_list, total_items, query_params):
    request = query_params["request"]
    query_string = request.query
    class_uri = 'http://{0}/{1}/{2}'.format(request.headers.get("Host"),
                                            query_params["context_name"],
                                            query_params["class_name"])
    json = {
        'items': items_list,
        'item_count': total_items,
        'links': [
            {
                'href': class_uri,
                'rel': "self"
            },
            {
                'href': "%s/{resource_id}" % class_uri,
                'rel': "item"
            },
            {
                'href': class_uri,
                'method': "POST",
                'rel': "create"
            },
            {
                'href': "%s?%s" % (class_uri, set_query_string_parameter(query_string, "page", "1")),
                'method': "GET",
                'rel': "first"
            }
        ]
    }
    return json
