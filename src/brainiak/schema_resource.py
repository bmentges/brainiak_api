# -*- coding: utf-8 -*-

import json
from brainiak.triplestore import query_sparql
from brainiak.result_handler import *
from brainiak import settings


def assemble_schema_dict(class_uri, title, predicates, **kw):
    response = {
        "type": "object",
        "@id": class_uri,
        "@context": {"@langauge": "pt"},
        "$schema": "http://json-schema.org/draft-03/schema#",
        "title": title,
        "properties": predicates
    }
    comment =  kw.get("comment", None)
    if comment:
        response["comment"] = comment 

    return response

def get_schema(context_name, schema_name, callback):
    class_uri = "/".join((settings.URI_PREFIX, context_name, schema_name))

    def has_predicates_and_cardinalities(class_schema, predicates_and_cardinalities):
        response_dict = assemble_schema_dict(class_uri,
                                             get_one_value(class_schema, "title"),
                                             predicates_and_cardinalities,
                                             comment=get_one_value(class_schema, "comment"))
        callback(response_dict)

    def has_class_schema(tornado_response):
        class_schema = json.loads(tornado_response.body)
        get_predicates_and_cardinalities(class_uri, class_schema, has_predicates_and_cardinalities)

    query_class_schema(class_uri, has_class_schema)

"""
    "links":[
        {
            "rel": "person:birthPlace",
            "title": "Local de Nascimento",
            "maxItems": 1,
            "type": "string",
            "format": "uri",
            "href": "place:Place",
            "rdfs:comment": "Local de nascimento de uma pessoa. Pode ser país, estado, cidade, etc."
        },
        {
            "rel": "person:cityOfBirth",
            "href": "substituir por URL da api de dados onde obter vocabulario para campo"
        },
        {
            "rel": "person:parent",
            "href": "substituir por URL da api de dados onde obter vocabulario para campo"
        },
        {
            "rel": "person:birthPlace",
            "href": "substituir por URL da api de dados onde obter vocabulario para campo"
        }
    ],
    "properties": {
        "person:cityOfBirth": {
            "title": "Naturalidade",
            "maxItems": 1,
            "type": "string",
            "format": "uri",
            "range": ["place:City"]
        },

        "person:parent": {
            "title": "Filiação",
            "type": "array",
            "items": {
                "type": "string",
                "format": "uri",
                "range": ["person:Person"]
            }
        },

        "person:birthPlace": {
            "title": "Local de Nascimento",
            "maxItems": 1,
            "type": "string",
            "format": "uri",
            "range": ["place:Place"],
            "rdfs:comment": "Local de nascimento de uma pessoa. Pode ser país, estado, cidade, etc."
        },
        
        "person:gender": {
            "title": "Sexo",
            "type": "string",
            "format": "uri",
            "enum": [ "gender:Male", "gender:Female:", "gender:Transgender" ],
            "minItems": 1,
            "maxItems": 1,
            "range": ["person:Gender"]
        },
        
        "upper:birthDate": {
            "title": "Data de Nascimento",
            "type": "string",
            "format": "date-time"
        },
        "upper:name": {
            "title": "Nome",
            "type": "string",
            "minItems": 1,
            "rdfs:comment": "Nomes populares de uma instância. Exemplo: nomes pelo quais uma pessoa é conhecida (e.g. Ronaldinho, Zico, Lula). Não confundir com nome completo, uma outra propriedade com valor único e formal."
        },
        "person:fullName": {
            "title": "Nome Completo",
            "type": "string",
            "maxItems": 1
        },
        "person:occupation": {
            "title": "Ocupação",
            "type": "string"
        },
        "person:mainPhoto": {
            "title": "Foto",
            "type": "string",
            "format": "uri"
        }
    }
}
"""

def get_predicates_and_cardinalities(class_uri, class_schema, callback):

    def has_cardinalities(tornado_response, class_schema, callback):
        cardinalities = json.loads(tornado_response.body)

        def has_predicates(tornado_response, class_schema=class_schema):
            predicates = json.loads(tornado_response.body)
            unique_predicates = _get_unique_predicates_list(predicates)
            predicates_dict = {}
            for predicate in unique_predicates:
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
                for item in _get_predicates_dict_for_a_predicate(predicates, predicate):
                    predicate_dict["type"] = item["type"]
                    predicate_dict["title"] = item["title"]
                    predicate_dict["graph"] = item["predicate_graph"]
                    if "predicate_comment" in item:  # Para Video que não tem isso
                        predicate_dict["comment"] = item["predicate_comment"]
                predicates_dict[predicate] = predicate_dict

            callback(class_schema, predicates_dict)

        query_predicates(class_uri, has_predicates)

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


def _get_predicates_dict_for_a_predicate(predicates, predicate):
    items = []
    parsed_item = {}
    for item in predicates['results']['bindings']:
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
            ranges[range_class_uri] = {'graph': range_graph, 'title': range_label}
            break
    return ranges


def query_class_schema(class_uri, callback):
    QUERY_TEMPLATE = """
        SELECT DISTINCT ?title ?comment
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?title . FILTER(langMatches(lang(?title), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri}
    # self.logger.info("%s" % QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)


def query_predicates(class_uri, callback):

    def fallback_query_callback(tornado_response):
        response = json.loads(tornado_response.body)
        if not response['results']['bindings']:
            _query_predicate_without_lang(class_uri, callback)
        else:
            callback(tornado_response)

    _query_predicate_with_lang(class_uri, fallback_query_callback)


def _query_predicate_with_lang(class_uri, callback):
    QUERY_TEMPLATE = """
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
    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)


def _query_predicate_without_lang(class_uri, callback):
    QUERY_TEMPLATE = """
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
    # self.logger.info(QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE)
