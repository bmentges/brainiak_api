from brainiak import triplestore
from brainiak.utils.params import LIST_PARAMS, RequiredParamsDict
from brainiak.utils.sparql import compress_keys_and_values

# QUERY_ANNOTATION = u"""
# SELECT COUNT(?class) AS ?total_items
# FROM <%(graph_uri)s>
# {
#     ?class a owl:Class ;
#            rdfs:label ?label .
#     %(lang_filter_label)s
# }
# """

QUERY_ANNOTATION = u"""
SELECT ?uri ?permalink FROM <{graph_uri}> WHERE {{
?uri a <{class_uri}>;
     base:status_de_publicacao "P";
     base:data_da_primeira_publicacao ?data_da_primeira_publicacao;
     base:permalink ?permalink;
     ?p <{uri}>.
}}ORDER BY {sort_order}(?data_da_primeira_publicacao)
limit {per_page}"""

ANNOTATIONS_PARAMS = LIST_PARAMS + RequiredParamsDict(uri="")


def query_annotation(query_params):
    query = QUERY_ANNOTATION.format(**query_params)
    return triplestore.query_sparql(query,
                                    query_params.triplestore_config)


def get_content_with_annotation(query_params):
    result = query_annotation(query_params)
    return compress_keys_and_values(result)
