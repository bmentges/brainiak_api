# -*- coding: utf-8 -*-

from brainiak.prefixes import MemorizeContext, shorten_uri, prefix_from_uri
from brainiak.utils.sparql import get_one_value
from brainiak.triplestore import query_sparql
from brainiak.type_mapper import DATATYPE_PROPERTY, items_from_type, items_from_range, OBJECT_PROPERTY


def get_schema(query_params):

    context = MemorizeContext()
    short_uri = context.shorten_uri(query_params["class_uri"])

    class_schema = query_class_schema(query_params)
    if not class_schema["results"]["bindings"]:
        return

    predicates_and_cardinalities = get_predicates_and_cardinalities(context, query_params)
    response_dict = assemble_schema_dict(query_params,
                                         short_uri,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         context,
                                         comment=get_one_value(class_schema, "comment"))
    return response_dict


def assemble_schema_dict(query_params, short_uri, title, predicates, context, **kw):
    effective_context = {"@language": query_params.get("lang")}
    effective_context.update(context.context)

    links = [{"rel": "create",
              "method": "POST",
              "href": "/{context_name}/{class_name}".format(**query_params)}]
    obj_property_links = [{"rel": property_name,
                           "href": "/{0}/{1}".format(*(uri.split(':')))}
                           for property_name, uri in context.object_properties.items()]

    links.extend(obj_property_links)

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


QUERY_FILTER_TITLE = 'FILTER(langMatches(lang(?title), "%s") or langMatches(lang(?title), "")) .'
QUERY_FILTER_COMMENT = 'FILTER(langMatches(lang(?comment), "%s") or langMatches(lang(?comment), "")) .'
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
    params["filter_title"] = (QUERY_FILTER_TITLE % lang) if lang else ""
    params["filter_comment"] = (QUERY_FILTER_COMMENT % lang) if lang else ""
    return QUERY_CLASS_SCHEMA % params


def query_class_schema(query_params):
    query = build_class_schema_query(query_params)
    return query_sparql(query)


def get_predicates_and_cardinalities(context, query_params):
    query_result = query_cardinalities(query_params)
    cardinalities = _extract_cardinalities(query_result['results']['bindings'])

    predicates = query_predicates(query_params)

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
    response = _query_predicate_with_lang(query_params)

    if not response['results']['bindings']:
        return _query_predicate_without_lang(query_params)
    else:
        return response


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
            FILTER(langMatches(lang(?title), "%(lang)s") or langMatches(lang(?title), "")) .
            FILTER(langMatches(lang(?predicate_comment), "%(lang)s") or langMatches(lang(?predicate_comment), "")) .
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


def build_predicate_dict(name, predicate, cardinalities, context):
    predicate_dict = {}
    predicate_type = predicate['type']['value']
    range_class_uri = predicate['range']['value']
    range_key = context.shorten_uri(range_class_uri)

    if predicate_type == OBJECT_PROPERTY:
        predicate_dict["range"] = {'@id': range_key,
                                   'graph': context.prefix_to_slug(predicate.get('grafo_do_range', {}).get('value', "")),
                                   'title': predicate.get('label_do_range', {}).get('value', "")}
        context.add_object_property(predicate['predicate']['value'], range_key)

    elif predicate_type == DATATYPE_PROPERTY:
        # Have a datatype property
        predicate_dict.update(items_from_range(range_class_uri))

    if (name in cardinalities) and (range_class_uri in cardinalities[name]):
        predicate_restriction = cardinalities[name]
        predicate_dict.update(predicate_restriction[range_class_uri])
        if "enum" in predicate_restriction:
            # FIXME: simplify value returned from cardinalities to avoid ugly code below
            predicate_dict["enum"] = predicate_restriction["enum"]

    simplified_predicate = {attribute: predicate[attribute]['value'] for attribute in predicate}
    add_items = items_from_type(simplified_predicate["type"])
    if add_items:
        predicate_dict.update(add_items)
    predicate_dict["title"] = simplified_predicate["title"]
    predicate_dict["graph"] = context.prefix_to_slug(simplified_predicate["predicate_graph"])
    if "predicate_comment" in simplified_predicate:  # Para Video que não tem isso
        predicate_dict["comment"] = simplified_predicate["predicate_comment"]
    return predicate_dict


def convert_bindings_dict(context, bindings, cardinalities):
    range_dict = {p['predicate']['value']: p['range']['value'] for p in bindings}

    predicates_dict = {}
    remove_super_predicates = []
    for predicate in bindings:
        predicate_name = predicate['predicate']['value']
        try:
            super_property = predicate['super_property']['value']
        except KeyError:
            super_property = None
        if (super_property in range_dict) and (range_dict[super_property] == predicate['range']['value']):
            remove_super_predicates.append(super_property)
        predicate_dict = build_predicate_dict(predicate_name, predicate, cardinalities, context)
        predicates_dict[context.shorten_uri(predicate_name)] = predicate_dict

    # Avoid enumerating redundant predicates when a more specific predicate prevails over
    # an inherited predicate with the same range
    for p in remove_super_predicates:
        del predicates_dict[shorten_uri(p)]

    return predicates_dict
