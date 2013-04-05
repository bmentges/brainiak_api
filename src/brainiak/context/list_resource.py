from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import add_language_support
from brainiak import triplestore
from brainiak.utils.sparql import compress_keys_and_values, get_one_value
from brainiak.utils.links import build_links
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

    decorate_with_resource_id(items_list)

    request = query_params["request"]
    base_url = 'http://{0}/{1}/'.format(request.headers.get("Host"),
                                        query_params["context_name"])

    links_section = build_links(
        base_url,
        page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
        per_page=int(query_params["per_page"]),
        request_url=request.uri,
        total_items=total_items,
        query_string=request.query)

    context_section = context.context
    context_section.update({"@language": query_params.get("lang")})

    json_dict = {
        'items': items_list,
        'item_count': total_items,
        'links': links_section,
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
