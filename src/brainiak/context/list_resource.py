from brainiak.utils.sparql import add_language_support, is_result_empty
from brainiak import triplestore


def list_classes(query_params):
    query_result_dict = query_classes_list(query_params)
    if is_result_empty(query_result_dict):
        return None
    else:
        return assemble_list_json(query_result_dict)


def assemble_list_json():
    pass


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
