from dateutil import parser
from brainiak import triplestore
from brainiak.utils.sparql import compress_keys_and_values
from brainiak.utils.resources import calculate_offset

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
SELECT ?subject ?label ?permalink ?issued FROM <{graph_uri}> WHERE {{
?subject a <{class_uri}> ;
         base:status_de_publicacao "P" ;
         ?p <{object_uri}> ;
         base:data_da_primeira_publicacao ?issued ;
         rdfs:label ?label ;
         base:permalink ?permalink .
{time_range_filter_clause}
}}
ORDER BY {sort_order}(?issued)
LIMIT {per_page}
OFFSET {offset}
"""


def query_annotation(query_params):

    query = QUERY_ANNOTATION.format(**query_params)
    return triplestore.query_sparql(query,
                                    query_params.triplestore_config)


def get_content_with_annotation(query_params):
    decorate_params_with_time_range_clause(query_params)
    query_params["offset"] = calculate_offset(query_params)

    # TODO filter class to only accept base:Conteudo
    result = query_annotation(query_params)

    keymap = {
        "subject": "@id",
        "label": "title",
    }

    # TODO decorate with JSON schema meta_properties
    items_list = compress_keys_and_values(result, keymap=keymap)
    return build_json(items_list, query_params)

def procDateTime(date):
    #return the given date in isoformat with Z
    #validate date and format e.g 2013-02-29 is format valid but is not a valid date
    #or 2013-02-28T25:00 is format valid but the hour is invalid
    dateObj = parser(date)
    return dateObj.isoformat() + "Z"

def decorate_params_with_time_range_clause(query_params):



    # TODO refactor to create a specific ParamDict
    clause = ""

    conditionals = []
    if query_params["from"]:
        query_params["from"] = procDateTime(query_params["from"])
        conditionals.append('?issued >= xsd:dateTime("{from}")'.format(**query_params))

    if query_params["to"]:
        query_params["to"] = procDateTime(query_params["to"])
        conditionals.append('?issued < xsd:dateTime("{to}")'.format(**query_params))

    if conditionals:
        clause = "FILTER(" + " && ".join(conditionals) + ")"

    query_params["time_range_filter_clause"] = clause


def build_json(items_list, query_params):
    return {
        "items": items_list
    }
