from brainiak import triplestore
from brainiak.utils.params import LIST_PARAMS, RequiredParamsDict


QUERY_ANNOTATION = u"""
SELECT COUNT(?class) AS ?total_items
FROM <%(graph_uri)s>
{
    ?class a owl:Class ;
           rdfs:label ?label .
    %(lang_filter_label)s
}
"""


ANNOTATIONS_PARAMS = LIST_PARAMS + RequiredParamsDict(annotation="")

def query_annotation(query_params):
    # query = QUERY_ANNOTATION % query_params
    # return triplestore.query_sparql(query,
    #                                 query_params.triplestore_config)
    pass

def get_content_with_annotation(query_params):
    return {}
