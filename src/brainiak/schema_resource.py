# -*- coding: utf-8 -*-

from brainiak.triplestore import query_sparql
from brainiak.result_handler import *
from brainiak import settings


def get_schema(context_name, schema_name, callback):
    class_uri = "/".join((settings.URI_PREFIX, context_name, schema_name))

    def has_predicates_and_cardinalities(class_schema, predicates_and_cardinalities):
        complete_dict = {"class": class_uri,
                         "label": get_one_value(class_schema, "label"),
                         "comment": get_one_value(class_schema, "comment"),
                         "predicates": predicates_and_cardinalities}
        callback(complete_dict)

    def has_class_schema(class_schema):
        get_predicates_and_cardinalities(class_uri, class_schema, has_predicates_and_cardinalities)

    query_class_schema(class_uri, has_class_schema)


def get_predicates_and_cardinalities(class_uri, class_schema, callback):

    def has_cardinalities(cardinalities, class_schema, callback):
        predicates = _get_unique_predicates_list(class_schema)
        predicates_dict = {}
        for predicate in predicates:
            new_ranges = {}
            predicate_dict = {}
            ranges = _get_ranges_for_predicate(predicates, predicate)
            for predicate_range in ranges:
                new_ranges[predicate_range] = ranges[predicate_range]
                if (predicate in cardinalities) and (predicate_range in cardinalities[predicate]):
                    predicate_restriction = cardinalities[predicate]
                    new_ranges[predicate_range].update(predicate_restriction[predicate_range])
                    if "options" in predicate_restriction:
                        new_ranges[predicate_range]["options"] = predicate_restriction["options"]

            predicate_dict["range"] = new_ranges
            for item in _get_predicates_dict_for_a_predicate(predicate, class_schema):
                predicate_dict["type"] = item["type"]
                predicate_dict["label"] = item["label"]
                predicate_dict["graph"] = item["predicate_graph"]
                if "predicate_comment" in item:  # Para Video que não tem isso
                    predicate_dict["comment"] = item["predicate_comment"]
            predicates_dict[predicate] = predicate_dict

        callback(predicates_dict)

    query_cardinalities(class_uri, class_schema, callback, has_cardinalities)


def query_cardinalities(class_uri, class_schema, final_callback, callback):
    QUERY_TEMPLATE = u"""
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
    }
    """ % {"class_uri": class_uri}
    # self.logger.info("%s" % str(QUERY))
    query_sparql(callback, QUERY_TEMPLATE, class_schema, final_callback)


def _get_unique_predicates_list(predicates):
    return sorted(list({item['predicate']['value'] for item in predicates['results']['bindings']}))


def _get_predicates_dict_for_a_predicate(predicate, class_schema):
    items = []
    parsed_item = {}
    for item in class_schema['results']['bindings']:
        if item['predicate']['value'] == predicate:
            for attribute in item:
                if attribute not in parsed_item:
                    parsed_item[attribute] = item[attribute]['value']
            items.append(parsed_item)
    return items


def _get_ranges_for_predicate(predicates, predicate):
    ranges = {}
    for item in predicates['results']['bindings']:
        if item['predicate']['value'] == predicate:
            range_class_uri = item['range']['value']
            range_label = item.get('label_do_range', {}).get('value', "")
            range_graph = item.get('grafo_do_range', {}).get('value', "")
            ranges[range_class_uri] = {'graph': range_graph, 'label': range_label}
    return ranges


def query_class_schema(class_uri, callback):
    QUERY_TEMPLATE = """
        SELECT DISTINCT ?label ?comment
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?label . FILTER(langMatches(lang(?label), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri}
    # self.logger.info("%s" % QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)


def query_predicates(class_uri, callback):

    def fallback_query_callback(response):
        if not response['results']['bindings']:
            _query_predicate_without_lang(class_uri, callback)
        else:
            callback(response)

    _query_predicate_with_lang(class_uri, fallback_query_callback)


def _query_predicate_with_lang(class_uri, callback):
    QUERY_TEMPLATE = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?label ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
        ?predicate rdfs:range ?range .
        ?predicate rdfs:label ?label .
        ?predicate rdf:type ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        FILTER(langMatches(lang(?label), "%(lang)s")) .
        FILTER(langMatches(lang(?predicate_comment), "%(lang)s")) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . FILTER(langMatches(lang(?label_do_range), "%(lang)s")) . } } .
        OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
    }""" % {'class_uri': class_uri, 'lang': 'PT'}
    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)


def _query_predicate_without_lang(class_uri, callback):
    QUERY_TEMPLATE = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?label ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        <%(class_uri)s> rdfs:subClassOf ?domain_class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
        ?predicate rdfs:range ?range .
        ?predicate rdfs:label ?label .
        ?predicate rdf:type ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . } } .
        OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
    }""" % {'class_uri': class_uri}
    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)
