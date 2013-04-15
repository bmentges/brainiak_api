from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import add_language_support
from brainiak import triplestore
from brainiak.utils.sparql import compress_keys_and_values, get_one_value
from brainiak.utils.resources import compress_duplicated_ids
from brainiak.utils.links import crud_links, add_link, collection_links
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

    request = query_params["request"]
    base_url = "{0}://{1}{2}".format(request.protocol, request.host, request.path)

    resource_url = "%s/{resource_id}" % normalize(base_url)
    links = crud_links(base_url, resource_url, query_params) + \
            collection_links(base_url, query_params, total_items)


    links = crud_links(base_url, query_string=request.query) + collection_links(
        base_url,
        query_string=request.query,
        page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
        per_page=int(query_params["per_page"]),
        total_items=total_items)

    # Per-service links
    add_link(links, 'type', "{base_url}/{{resource_id}}/_schema", base_url=base_url)

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
