# -*- coding: utf-8 -*-
import json

from tornado import gen

from brainiak import settings
from brainiak.prefixes import MemorizeContext, shorten_uri, prefix_from_uri
from brainiak.result_handler import get_one_value, convert_bindings_dict
from brainiak.triplestore import query_sparql


def get_schema(context_name, schema_name):
    class_uri = settings.URI_PREFIX + "/".join((context_name, schema_name))

    context = MemorizeContext()
    short_uri = context.shorten_uri(class_uri)

    tornado_response = query_class_schema(class_uri, context)
    class_schema = json.loads(tornado_response.body)
    if not class_schema["results"]["bindings"]:
        return

    predicates_and_cardinalities = get_predicates_and_cardinalities(class_uri, class_schema, context)
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


def query_class_schema(class_uri, context):
    query = """
        SELECT DISTINCT ?title ?comment
        FROM <%(graph_uri)s>
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?title . FILTER(langMatches(lang(?title), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri, "graph_uri": prefix_from_uri(class_uri)}
    return query_sparql(query, context)


def get_predicates_and_cardinalities(class_uri, class_schema, context):
    response = query_cardinalities(class_uri, class_schema, context)
    tornado_response = response
    query_result = json.loads(tornado_response.body)
    cardinalities = _extract_cardinalities(query_result['results']['bindings'])

    response = query_predicates(class_uri, context)
    tornado_response = response
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


def query_cardinalities(class_uri, class_schema, context):
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
        }""" % {"class_uri": class_uri}
    return query_sparql(query, class_schema, context)


def query_predicates(class_uri, context):
    resp = _query_predicate_with_lang(class_uri, context)
    tornado_response = resp

    response = json.loads(tornado_response.body)
    if not response['results']['bindings']:
        return _query_predicate_without_lang(class_uri, context)
    else:
        return tornado_response


def _query_predicate_with_lang(class_uri, context):
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
        }""" % {'class_uri': class_uri, 'lang': 'PT'}
    return query_sparql(query, context)


def _query_predicate_without_lang(class_uri, context):
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
        }""" % {'class_uri': class_uri}
    return query_sparql(query, context)
