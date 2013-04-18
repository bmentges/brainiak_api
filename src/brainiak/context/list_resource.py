from brainiak import triplestore
from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import add_language_support
from brainiak.utils.sparql import compress_keys_and_values, get_one_value
from brainiak.utils.resources import compress_duplicated_ids
from brainiak.utils.links import crud_links, add_link, collection_links, remove_last_slash
from brainiak.prefixes import MemorizeContext


def list_classes(query_params):
    (query_params, language_tag) = add_language_support(query_params, "label")
    count_query_result_dict = query_count_classes(query_params)

    total_items = int(get_one_value(count_query_result_dict, "total_items"))

    if not total_items:
        return None
    else:
        query_result_dict = query_classes_list(query_params)
        return assemble_list_json(query_params, query_result_dict, total_items)


def assemble_list_json(query_params, query_result_dict, total_items):
    context = MemorizeContext()
    items_list = compress_keys_and_values(
        query_result_dict,
        keymap={"class": "@id", "label": "title"},
        context=context)
    items_list = compress_duplicated_ids(items_list)

    decorate_with_resource_id(items_list)

    links = crud_links(query_params) + collection_links(query_params, total_items)

    # Per-service links
    add_link(links, 'type', "{base_url}/{{resource_id}}/_schema", base_url=remove_last_slash(query_params.base_url))

    context_section = context.context
    context_section.update({"@language": query_params.get("lang")})

    json_dict = {
        'items': items_list,
        'item_count': total_items,
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
OFFSET %(page)s
"""


def query_classes_list(query_params):
    query = QUERY_ALL_CLASSES_OF_A_GRAPH % query_params
    return triplestore.query_sparql(query)
