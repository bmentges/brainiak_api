# -*- coding: utf-8 -*-

from brainiak.prefixes import MemorizeContext, shorten_uri
from brainiak.utils.sparql import get_one_value, filter_values, add_language_support
from brainiak import triplestore
from brainiak.type_mapper import DATATYPE_PROPERTY, items_from_type, items_from_range, OBJECT_PROPERTY


def get_schema(query_params):

    context = MemorizeContext()
    short_uri = context.shorten_uri(query_params["class_uri"])

    class_schema = query_class_schema(query_params)
    if not class_schema["results"]["bindings"]:
        return

    query_params["superclasses"] = query_superclasses(query_params)
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


QUERY_CLASS_SCHEMA = """
SELECT DISTINCT ?title ?comment
FROM <%(graph_uri)s>
WHERE {
    <%(class_uri)s> a owl:Class ;
                    rdfs:label ?title .
    %(lang_filter_title)s
    OPTIONAL {<%(class_uri)s> rdfs:comment ?comment .
    %(lang_filter_comment)s} .
}
"""


def build_class_schema_query(params):
    """
    Note: if params["lang"] is not False (e.g. "pt"), the following variables
    are filtered according to the lang provided:
    - rdfs:label
    - rdfs:comment (optional)
    """
    (params, language_tag) = add_language_support(params, "title")
    (params, language_tag) = add_language_support(params, "comment")
    return QUERY_CLASS_SCHEMA % params


def query_class_schema(query_params):
    query = build_class_schema_query(query_params)
    return triplestore.query_sparql(query)


def get_predicates_and_cardinalities(context, query_params):
    (query_params, language_tag) = add_language_support(query_params, "enumerated_value_label")
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
                OPTIONAL {
                    ?enumerated_value rdfs:label ?enumerated_value_label .
                    %(lang_filter_enumerated_value_label)s
                } .
            }
        }""" % query_params
    return triplestore.query_sparql(query)


def query_predicates(query_params):
    response = _query_predicate_with_lang(query_params)

    if not response['results']['bindings']:
        return _query_predicate_without_lang(query_params)
    else:
        return response


def _query_predicate_with_lang(query_params):
    query_params["filter_classes_clause"] = "FILTER (?domain_class IN (<" + ">, <".join(query_params["superclasses"]) + ">))"

    query = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        {
          GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
        } UNION {
          graph ?predicate_graph {?predicate rdfs:domain ?blank} .
          ?blank a owl:Class .
          ?blank owl:unionOf ?enumeration .
          OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
          OPTIONAL { ?list_node rdf:first ?domain_class } .
        }
        %(filter_classes_clause)s
        {?predicate rdfs:range ?range .}
        UNION {
          ?predicate rdfs:range ?blank .
          ?blank a owl:Class .
          ?blank owl:unionOf ?enumeration .
          OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
          OPTIONAL { ?list_node rdf:first ?range } .
        }
        FILTER (!isBlank(?range))
        ?predicate rdfs:label ?title .
        ?predicate rdf:type ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        FILTER(langMatches(lang(?title), "%(lang)s") or langMatches(lang(?title), "")) .
        FILTER(langMatches(lang(?predicate_comment), "%(lang)s") or langMatches(lang(?predicate_comment), "")) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . FILTER(langMatches(lang(?label_do_range), "%(lang)s")) . } } .
        OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
    }""" % query_params
    return triplestore.query_sparql(query)


def _query_predicate_without_lang(query_params):
    query_params["filter_classes_clause"] = "FILTER (?domain_class IN (<" + ">, <".join(query_params["superclasses"]) + ">))"
    query = """
    SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?grafo_do_range ?label_do_range ?super_property
    WHERE {
        {
          GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
        } UNION {
          graph ?predicate_graph {?predicate rdfs:domain ?blank} .
          ?blank a owl:Class .
          ?blank owl:unionOf ?enumeration .
          OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
          OPTIONAL { ?list_node rdf:first ?domain_class } .
        }
        %(filter_classes_clause)s
        {?predicate rdfs:range ?range .}
        UNION {
          ?predicate rdfs:range ?blank .
          ?blank a owl:Class .
          ?blank owl:unionOf ?enumeration .
          OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
          OPTIONAL { ?list_node rdf:first ?range } .
        }
        FILTER (!isBlank(?range))
        ?predicate rdfs:label ?title .
        ?predicate rdf:type ?type .
        OPTIONAL { ?predicate owl:subPropertyOf ?super_property } .
        FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
        OPTIONAL { GRAPH ?grafo_do_range {  ?range rdfs:label ?label_do_range . } } .
        OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
    }""" % query_params
    return triplestore.query_sparql(query)


def query_superclasses(query_params):
    result_dict = _query_superclasses(query_params)
    superclasses = filter_values(result_dict, "class")
    return superclasses


def _query_superclasses(query_params):
    query = """
    SELECT DISTINCT ?class
    WHERE {
        <%(class_uri)s> rdfs:subClassOf ?class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
        ?class a owl:Class .
    }
    """ % query_params
    return triplestore.query_sparql(query)


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


def join_predicates(old_predicates, new_predicate):

    new_format = new_predicate.get('format', '')
    new_range = new_predicate.get('range', {})
    new_type = new_predicate['type']

    old_format = old_predicates.get('format', '')
    old_range = old_predicates.get('range', {})
    old_type = old_predicates['type']

    old_range_is_list = isinstance(old_range, list)

    if (new_type == old_type) and (new_format == old_format):
        if old_range_is_list:
            old_range.append(new_range)
        else:
            old_range = [old_range, new_range]
    else:
        if not old_range_is_list:
            old_range = [old_range]

        for each_range in old_range:
            each_range['type'] = old_type
            each_range['format'] = old_format

        new_range['type'] = new_type
        new_range['range'] = new_range
        old_range.append(new_range)
        new_predicate['type'] = ''
        new_predicate['format'] = ''

    new_predicate['range'] = old_range
    return new_predicate


def convert_bindings_dict(context, bindings, cardinalities):

    # range_dict = {}
    # for item in bindings:
    #     item_predicate = item['predicate']['value']
    #     item_range = item.get('range', {}).get('value', {})
    #     existing_range = range_dict.get(item_predicate, [])
    #     if item_range not in existing_range:
    #         existing_range.append(item_range)
    #         range_dict[item_predicate] = existing_range

    super_predicates = [item['super_property']['value'] for item in bindings if 'super_property' in item]

    predicates_dict = {}

    for predicate in bindings:
        predicate_name = predicate['predicate']['value']
        if not predicate_name in super_predicates:

            shorten_predicate_name = context.shorten_uri(predicate_name)
            predicate_dict = build_predicate_dict(predicate_name, predicate, cardinalities, context)

            if shorten_predicate_name in predicates_dict:
                previous_predicates = predicates_dict[shorten_predicate_name]
                if previous_predicates != predicate_dict:
                    predicates_dict[shorten_predicate_name] = join_predicates(previous_predicates, predicate_dict)
            else:
                predicates_dict[shorten_predicate_name] = predicate_dict

    return predicates_dict
