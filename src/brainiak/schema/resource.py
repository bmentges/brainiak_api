# -*- coding: utf-8 -*-
import json

from tornado import gen

from brainiak import settings
from brainiak.prefixes import MemorizeContext, shorten_uri, prefix_from_uri
from brainiak.result_handler import get_one_value, convert_bindings_dict
from brainiak.triplestore import query_sparql


def get_schema(query_params):

    context = MemorizeContext()
    short_uri = context.shorten_uri(query_params["class_uri"])

    tornado_response = query_class_schema(query_params)
    class_schema = json.loads(tornado_response.body)
    if not class_schema["results"]["bindings"]:
        return

    predicates_and_cardinalities = get_predicates_and_cardinalities(context, query_params)
    response_dict = assemble_schema_dict(short_uri,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         context,
                                         comment=get_one_value(class_schema, "comment"))
    return response_dict


def assemble_schema_dict(short_uri, title, predicates, context, **kw):
    effective_context = {"@language": "pt"}
    effective_context.update(context.context)

    links = [{"rel": property_name,
              "href": "/{0}/{1}".format(*(uri.split(':')))}
             for property_name, uri in context.object_properties.items()]
    schema = {
        "type": "object",
        "@id": short_uri,
        "@context": effective_context,
        "$schema": "http://json-schema.org/draft-03/schema#",
        "title": title,
        "links": links,
        "properties": predicates
    }
    comment = kw.get("comment", None)
    if comment:
        schema["comment"] = comment

    return schema


QUERY_FILTER_TITLE = 'FILTER(langMatches(lang(?title), "%s")) .'
QUERY_FILTER_COMMENT = 'FILTER(langMatches(lang(?comment), "%s")) .'
QUERY_CLASS_SCHEMA = """
SELECT DISTINCT ?title ?comment
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> a owl:Class ;
                    rdfs:label ?title . %(filter_title)s
    OPTIONAL {<%(class_uri)s> rdfs:comment ?comment . %(filter_comment)s} .
}
"""


def build_class_schema_query(params):
    """
    Note: if params["lang"] is not False (e.g. "pt"), the following variables
    are filtered according to the lang provided:
    - rdfs:label
    - rdfs:comment (optional)
    """
    lang = params["lang"]
    params["filter_title"] = QUERY_FILTER_TITLE % lang if lang else ""
    params["filter_comment"] = QUERY_FILTER_COMMENT % lang if lang else ""
    return QUERY_CLASS_SCHEMA % params


def query_class_schema(query_params):
    query = build_class_schema_query(query_params)
    return query_sparql(query)


def get_predicates_and_cardinalities(context, query_params):
    tornado_response = query_cardinalities(query_params)
    query_result = json.loads(tornado_response.body)
    cardinalities = _extract_cardinalities(query_result['results']['bindings'])

    tornado_response = query_predicates(query_params)
    predicates = json.loads(tornado_response.body)

    return convert_bindings_dict(context, predicates['results']['bindings'], cardinalities)


def _extract_cardinalities(bindings):
    cardinalities = {}
    for binding in bindings:
        property_ = binding["predicate"]["value"]
        range_ = binding["range"]["value"]

        if not property_ in cardinalities:
            cardinalities[property_] = {}

        if not range_ in cardinalities[property_] and not range_.startswith("nodeID://"):
            cardinalities[property_][range_] = {}

        current_property = cardinalities[property_]

        if "min" in binding:
            current_property[range_].update({"minItems": binding["min"]["value"]})
        elif "max" in binding:
            current_property[range_].update({"maxItems": binding["max"]["value"]})
        elif "enumerated_value" in binding:
            new_options = current_property.get("enum", [])
            new_options.append(binding["enumerated_value"]["value"])
            current_property["enum"] = new_options

    return cardinalities


def query_cardinalities(query_params):
    query = """
        SELECT DISTINCT ?predicate ?min ?max ?range ?enumerated_value ?enumerated_value_label
        WHERE {
            <%(class_uri)s> rdfs:subClassOf ?s OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
            ?s owl:onProperty ?predicate .
            OPTIONAL { ?s owl:minQualifiedCardinality ?min } .
            OPTIONAL { ?s owl:maxQualifiedCardinality ?max } .
            OPTIONAL {
                { ?s owl:onClass ?range }
                UNION { ?s owl:onDataRange ?range }
                UNION { ?s owl:allValuesFrom ?range }
                OPTIONAL { ?range owl:oneOf ?enumeration } .
                OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
                OPTIONAL { ?list_node rdf:first ?enumerated_value } .
                OPTIONAL { ?enumerated_value rdfs:label ?enumerated_value_label } .
            }
        }""" % query_params
    return query_sparql(query)


def query_predicates(query_params):
    resp = _query_predicate_with_lang(query_params)
    tornado_response = resp

    response = json.loads(tornado_response.body)
    if not response['results']['bindings']:
        return _query_predicate_without_lang(query_params)
    else:
        return tornado_response


def _query_predicate_with_lang(query_params):
    query = """
        SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
        WHERE {
            <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
            GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
            ?predicate rdfs:range ?range .
            ?predicate rdfs:label ?title .
            ?predicate rdf:type ?type .
            OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
            FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
            FILTER(langMatches(lang(?title), "%(lang)s")) .
            FILTER(langMatches(lang(?predicate_comment), "%(lang)s")) .
            OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . FILTER(langMatches(lang(?label_do_range), "%(lang)s")) . } } .
            OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
        }""" % query_params
    return query_sparql(query)


def _query_predicate_without_lang(query_params):
    query = """
        SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
        WHERE {
            <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
            GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
            ?predicate rdfs:range ?range .
            ?predicate rdfs:label ?title .
            ?predicate rdf:type ?type .
            OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
            FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
            OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . } } .
            OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
        }""" % query_params
    return query_sparql(query)
