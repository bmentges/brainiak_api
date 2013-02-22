# -*- coding: utf-8 -*-

import json
from tornado import gen
from tornado.web import asynchronous
from brainiak.prefixes import MemorizeContext
from brainiak.triplestore import query_sparql
from brainiak.result_handler import *
from brainiak import settings
from brainiak.type_mapper import items_from_type, OBJECT_PROPERTY, DATATYPE_PROPERTY, items_from_range


def assemble_schema_dict(short_uri, title, predicates, remember, **kw):
    effective_context = {"@language": "pt"}
    effective_context.update(remember.context)

    links = [{"rel":"{0}:{1}".format(ctx, item),
              "href":"/{0}/collection/{1}".format(ctx, item)}
             for ctx, item in remember.object_properties]
    response = {
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
        response["comment"] = comment

    return response

@gen.engine
def get_schema(context_name, schema_name, callback):
    class_uri = "/".join((settings.URI_PREFIX, context_name, schema_name))
    remember = MemorizeContext()
    short_uri = remember.shorten_uri(class_uri)

    response = yield gen.Task(query_class_schema, class_uri, remember)
    tornado_response = response.args[0]
    class_schema = json.loads(tornado_response.body)

    response = yield gen.Task(get_predicates_and_cardinalities, class_uri, class_schema, remember)
    class_schema, predicates_and_cardinalities = response.args
    response_dict = assemble_schema_dict(short_uri,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         remember,
                                         comment=get_one_value(class_schema, "comment"))
    callback(response_dict)


def query_class_schema(class_uri, remember, callback):
    QUERY_TEMPLATE = """
        SELECT DISTINCT ?title ?comment
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?title . FILTER(langMatches(lang(?title), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri}
    # self.logger.info("%s" % QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE, remember)


def get_predicates_and_cardinalities(class_uri, class_schema, remember, callback):

    def has_cardinalities(tornado_response, class_schema, callback, remember):
        cardinalities = _extract_cardinalities(json.loads(tornado_response.body))

        def has_predicates(tornado_response, remember, class_schema=class_schema):
            predicates = json.loads(tornado_response.body)
            unique_predicates = _get_unique_predicates(predicates)
            predicates_dict = {}
            for predicate in unique_predicates:
                predicate_name = predicate['predicate']['value']
                predicate_dict = {}

                predicate_type = predicate['type']['value']
                range_class_uri = predicate['range']['value']
                range_key = remember.shorten_uri(range_class_uri)
                if predicate_type == OBJECT_PROPERTY:
                    predicate_dict["range"] = {'@id': range_key,
                                                'graph': remember.prefix_to_slug(predicate.get('grafo_do_range', {}).get('value', "")),
                                                'title': predicate.get('label_do_range', {}).get('value', "")}
                    remember.add_object_property(range_key)
                elif predicate_type == DATATYPE_PROPERTY:
                    # Have a datatype property
                    predicate_dict.update(items_from_range(range_class_uri))

                if (predicate_name in cardinalities) and (range_class_uri in cardinalities[predicate_name]):
                    predicate_restriction = cardinalities[predicate_name]
                    predicate_dict.update(predicate_restriction[range_class_uri])
                    if "options" in predicate_restriction:
                        predicate_dict["options"] = predicate_restriction["options"]

                for item in _get_predicates_dict_for_a_predicate(predicate):
                    add_items = items_from_type(item["type"])
                    if add_items:
                        predicate_dict.update(add_items)
                    predicate_dict["title"] = item["title"]
                    predicate_dict["graph"] = remember.prefix_to_slug(item["predicate_graph"])
                    if "predicate_comment" in item:  # Para Video que não tem isso
                        predicate_dict["comment"] = item["predicate_comment"]

                predicates_dict[remember.shorten_uri(predicate_name)] = predicate_dict

            callback(class_schema, predicates_dict)

        query_predicates(class_uri, remember, has_predicates)

    query_cardinalities(class_uri, class_schema, callback, remember, has_cardinalities)


def _extract_cardinalities(cardinalities_from_virtuoso):
    cardinalities = {}
    for binding in cardinalities_from_virtuoso['results']['bindings']:
        property_ = binding["predicate"]["value"]
        range_ = binding["range"]["value"]

        if (not property_ in cardinalities or
                not range_ in cardinalities[property_]) and \
                not range_.startswith("nodeID://"):
            cardinalities[property_] = {range_: {}}

        if "min" in binding:
            cardinalities[property_][range_].update({"minItems": binding["min"]["value"]})
        elif "max" in binding:
            cardinalities[property_][range_].update({"maxItems": binding["max"]["value"]})
        elif "enumerated_value" in binding:
            new_options = cardinalities[property_].get("options", [])
            new_options_entry = {binding["enumerated_value"]["value"]: binding.get("enumerated_value_label", "").get("value", "")}
            new_options.append(new_options_entry)
            cardinalities[property_].update({"options": new_options})

    return cardinalities


def query_cardinalities(class_uri, class_schema, final_callback, remember, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, class_schema, final_callback, remember)


def _get_unique_predicates(predicates):
    return {item['predicate']['value']: item for item in predicates['results']['bindings']}.values()


def _get_predicates_dict_for_a_predicate(predicate):
    items = []
    parsed_item = {}
    for attribute in predicate:
        if attribute not in parsed_item:
            parsed_item[attribute] = predicate[attribute]['value']
    items.append(parsed_item)
    return items


def query_predicates(class_uri, remember, callback):

    def fallback_query_callback(tornado_response, remember):
        response = json.loads(tornado_response.body)
        if not response['results']['bindings']:
            _query_predicate_without_lang(class_uri, remember, callback)
        else:
            callback(tornado_response, remember)

    _query_predicate_with_lang(class_uri, remember, fallback_query_callback)


def _query_predicate_with_lang(class_uri, remember, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, remember)


def _query_predicate_without_lang(class_uri, remember, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, remember)

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
