from brainiak import triplestore, settings
from brainiak.utils.links import remove_last_slash
from brainiak.utils.resources import decorate_with_class_prefix, decorate_with_resource_id, decorate_dict_with_pagination
from brainiak.utils.sparql import add_language_support, compress_keys_and_values, get_one_value
from brainiak.utils.resources import compress_duplicated_ids, calculate_offset
from brainiak.prefixes import MemorizeContext


def list_classes(query_params):
    (query_params, language_tag) = add_language_support(query_params, "label")
    query_result_dict = query_classes_list(query_params)
    if not query_result_dict or not query_result_dict['results']['bindings']:
        return None
    return assemble_list_json(query_params, query_result_dict)


def assemble_list_json(query_params, query_result_dict):
    context = MemorizeContext()
    expand_uri = bool(int(query_params.get('expand_uri', '0')))
    items_list = compress_keys_and_values(
        query_result_dict,
        keymap={"class": "@id", "label": "title"},
        context=context,
        expand_uri=expand_uri)
    items_list = compress_duplicated_ids(items_list)
    decorate_with_resource_id(items_list)
    decorate_with_class_prefix(items_list)

    context_section = context.context
    context_section.update({"@language": query_params.get("lang")})

    json_dict = {
        '_base_url': remove_last_slash(query_params.base_url),
        'items': items_list,
        '@context': context_section,
        '@id': query_params['graph_uri']
    }

    def calculate_total_items():
        count_query_result_dict = query_count_classes(query_params)
        total_items = int(get_one_value(count_query_result_dict, "total_items"))
        return total_items
    decorate_dict_with_pagination(json_dict, query_params, calculate_total_items)

    return json_dict

QUERY_COUNT_ALL_CLASSES_OF_A_GRAPH = """
SELECT COUNT(?class) AS ?total_items
FROM <%(graph_uri)s>
{
    ?class a owl:Class ;
           rdfs:label ?label .
    %(lang_filter_label)s
}
"""


def query_count_classes(query_params):
    query = QUERY_COUNT_ALL_CLASSES_OF_A_GRAPH % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


QUERY_ALL_CLASSES_OF_A_GRAPH = """
SELECT ?class ?label
FROM <%(graph_uri)s>
{
    ?class a owl:Class ;
           rdfs:label ?label .
    %(lang_filter_label)s
}
LIMIT %(per_page)s
OFFSET %(offset)s
"""


def query_classes_list(query_params):
    offset = calculate_offset(query_params)
    query_params['offset'] = offset
    query = QUERY_ALL_CLASSES_OF_A_GRAPH % query_params
    del query_params['offset']
    return triplestore.query_sparql(query, query_params.triplestore_config)
