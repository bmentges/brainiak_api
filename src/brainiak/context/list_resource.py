from brainiak.utils.sparql import add_language_support, is_result_empty
from brainiak import triplestore
from brainiak.utils.sparql import compress_keys_and_values
from brainiak.prefixes import MemorizeContext


def list_classes(query_params):
    query_result_dict = query_classes_list(query_params)
    if is_result_empty(query_result_dict):
        return None
    else:
        return assemble_list_json(query_result_dict)


def assemble_list_json(query_result_dict):
    context = MemorizeContext()
    json_dict = compress_keys_and_values(query_result_dict,
                                         keymap={"class": "@id", "label": "title"},
                                         context=context)
#    links_section = get_links()
#    links = build_links(
#        class_url,
#        page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
#        per_page=int(query_params["per_page"]),
#        request_uri=request.uri,
#        total_items=total_items,
#        query_string=request.query)


    json_dict.extend(links_section)


QUERY_ALL_CLASSES_OF_A_GRAPH = """
SELECT ?class ?label
FROM <%(graph_uri)s>
{
    ?class a owl:Class ;
           rdfs:label ?label .
    %(lang_filter_label)s
}
"""


def query_classes_list(query_params):
    (query_params, language_tag) = add_language_support(query_params, "label")
    query = QUERY_ALL_CLASSES_OF_A_GRAPH % query_params
    return triplestore.query_sparql(query)
