from brainiak import triplestore, settings
from brainiak.utils.resources import decorate_with_class_prefix, decorate_with_resource_id
from brainiak.utils.sparql import add_language_support, calculate_offset
from brainiak.utils.sparql import compress_keys_and_values
from brainiak.utils.resources import compress_duplicated_ids
from brainiak.utils.links import add_link, collection_links, remove_last_slash, self_link
from brainiak.prefixes import MemorizeContext


def list_classes(query_params):
    (query_params, language_tag) = add_language_support(query_params, "label")
    query_result_dict = query_classes_list(query_params)
    if not query_result_dict or not query_result_dict['results']['bindings']:
        return None
    return assemble_list_json(query_params, query_result_dict)


def assemble_list_json(query_params, query_result_dict):
    context = MemorizeContext()
    items_list = compress_keys_and_values(
        query_result_dict,
        keymap={"class": "@id", "label": "title"},
        context=context)
    items_list = compress_duplicated_ids(items_list)

    decorate_with_resource_id(items_list)
    decorate_with_class_prefix(items_list)

    links = self_link(query_params) + collection_links(query_params)
    add_link(links, 'instances', "{0}/{{resource_id}}?class_prefix={{class_prefix}}".format(remove_last_slash(query_params.base_url)))

    context_section = context.context
    context_section.update({"@language": query_params.get("lang")})

    json_dict = {
        'items': items_list,
        'links': links,
        '@context': context_section
    }

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
    return triplestore.query_sparql(query)


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
    offset = calculate_offset(query_params, settings.DEFAULT_PAGE, settings.DEFAULT_PER_PAGE)
    query_params['offset'] = offset
    query = QUERY_ALL_CLASSES_OF_A_GRAPH % query_params
    del query_params['offset']
    return triplestore.query_sparql(query)
