# -*- coding: utf-8 -*-

import json
from tornado import gen
from brainiak.prefixes import MemorizeContext
from brainiak.triplestore import query_sparql
from brainiak.result_handler import *
from brainiak import settings
from brainiak.type_mapper import items_from_type, OBJECT_PROPERTY, DATATYPE_PROPERTY, items_from_range


def assemble_schema_dict(short_uri, title, predicates, context, **kw):
    effective_context = {"@language": "pt"}
    effective_context.update(context.context)

    links = [{"rel": "{0}:{1}".format(ctx, item),
              "href": "/{0}/collection/{1}".format(ctx, item)}
             for ctx, item in context.object_properties]
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

    response = {"schema": schema}

    return response


@gen.engine
def get_schema(context_name, schema_name, callback):
    class_uri = "/".join((settings.URI_PREFIX, context_name, schema_name))
    context = MemorizeContext()
    short_uri = context.shorten_uri(class_uri)

    response = yield gen.Task(query_class_schema, class_uri, context)
    tornado_response = response.args[0]
    class_schema = json.loads(tornado_response.body)

    response = yield gen.Task(get_predicates_and_cardinalities, class_uri, class_schema, context)
    class_schema, predicates_and_cardinalities = response.args

    response_dict = assemble_schema_dict(short_uri,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         context,
                                         comment=get_one_value(class_schema, "comment"))
    callback(response_dict)


def query_class_schema(class_uri, context, callback):
    QUERY_TEMPLATE = """
        SELECT DISTINCT ?title ?comment
        WHERE {
            <%(class_uri)s> a owl:Class .
            {<%(class_uri)s> rdfs:label ?title . FILTER(langMatches(lang(?title), "PT")) . }
            {<%(class_uri)s> rdfs:comment ?comment . FILTER(langMatches(lang(?comment), "PT")) .}
        }
        """ % {"class_uri": class_uri}
    # self.logger.info("%s" % QUERY_TEMPLATE)
    query_sparql(callback, QUERY_TEMPLATE, context)


@gen.engine
def get_predicates_and_cardinalities(class_uri, class_schema, context, callback):
    response = yield gen.Task(query_cardinalities, class_uri, class_schema, callback, context)
    tornado_response, class_schema, callback, context = response.args

    query_result = json.loads(tornado_response.body)
    cardinalities = _extract_cardinalities(query_result['results']['bindings'])

    response = yield gen.Task(query_predicates, class_uri, context)
    tornado_response, context = response.args
    predicates = json.loads(tornado_response.body)
    predicate_definitions = predicates['results']['bindings']
    predicates_dict = {}
    for predicate in predicate_definitions:
        predicate_name = predicate['predicate']['value']
        predicate_dict = build_predicate_dict(predicate_name, predicate, cardinalities, context)
        predicates_dict[context.shorten_uri(predicate_name)] = predicate_dict

    callback(class_schema, predicates_dict)


def build_predicate_dict(name, predicate, cardinalities, context):
    predicate_dict = {}
    predicate_type = predicate['type']['value']
    range_class_uri = predicate['range']['value']
    range_key = context.shorten_uri(range_class_uri)

    if predicate_type == OBJECT_PROPERTY:
        predicate_dict["range"] = {'@id': range_key,
                                   'graph': context.prefix_to_slug(predicate.get('grafo_do_range', {}).get('value', "")),
                                   'title': predicate.get('label_do_range', {}).get('value', "")}
        context.add_object_property(range_key)

    elif predicate_type == DATATYPE_PROPERTY:
        # Have a datatype property
        predicate_dict.update(items_from_range(range_class_uri))

    if (name in cardinalities) and (range_class_uri in cardinalities[name]):
        predicate_restriction = cardinalities[name]
        predicate_dict.update(predicate_restriction[range_class_uri])
        if "options" in predicate_restriction:
            # FIXME: simplify value returned from cardinalities to avoid ugly code below
            predicate_dict["enum"] = [context.shorten_uri(d.keys()[0]) for d in predicate_restriction["options"]]

    for item in _get_predicates_dict_for_a_predicate(predicate):
        add_items = items_from_type(item["type"])
        if add_items:
            predicate_dict.update(add_items)
        predicate_dict["title"] = item["title"]
        predicate_dict["graph"] = context.prefix_to_slug(item["predicate_graph"])
        if "predicate_comment" in item:  # Para Video que não tem isso
            predicate_dict["comment"] = item["predicate_comment"]
    return predicate_dict


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
            new_options = current_property.get("options", [])
            new_options_entry = {binding["enumerated_value"]["value"]: binding.get("enumerated_value_label", "").get("value", "")}
            new_options.append(new_options_entry)
            current_property.update({"options": new_options})

    return cardinalities


def query_cardinalities(class_uri, class_schema, final_callback, context, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, class_schema, final_callback, context)


def _get_predicates_dict_for_a_predicate(predicate):
    items = []
    parsed_item = {}
    for attribute in predicate:
        if attribute not in parsed_item:
            parsed_item[attribute] = predicate[attribute]['value']
    items.append(parsed_item)
    return items


@gen.engine
def query_predicates(class_uri, context, callback):
    resp = yield gen.Task(_query_predicate_with_lang, class_uri, context)
    tornado_response, context = resp.args
    response = json.loads(tornado_response.body)
    if not response['results']['bindings']:
        _query_predicate_without_lang(class_uri, context, callback)
    else:
        callback(tornado_response, context)


def _query_predicate_with_lang(class_uri, context, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, context)


def _query_predicate_without_lang(class_uri, context, callback):
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
    query_sparql(callback, QUERY_TEMPLATE, context)
