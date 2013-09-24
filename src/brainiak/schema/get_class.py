# -*- coding: utf-8 -*-

from brainiak.prefixes import MemorizeContext
from brainiak.utils.links import assemble_url, add_link, self_url, crud_links, remove_last_slash
from brainiak.utils.sparql import add_language_support, filter_values, get_one_value, get_super_properties
from brainiak import triplestore
from brainiak.type_mapper import DATATYPE_PROPERTY, OBJECT_PROPERTY, _MAP_XSD_TO_JSON_TYPE


def get_cached_schema(query_params):
    return get_schema(query_params)


def get_schema(query_params):

    context = MemorizeContext(normalize_keys=query_params['expand_uri_keys'],
                              normalize_values=query_params['expand_uri_values'])

    class_schema = query_class_schema(query_params)
    if not class_schema["results"]["bindings"]:
        return

    normalized_uri = context.normalize_uri_value(query_params["class_uri"])

    query_params["superclasses"] = query_superclasses(query_params)
    predicates_and_cardinalities = get_predicates_and_cardinalities(context, query_params)
    response_dict = assemble_schema_dict(query_params,
                                         normalized_uri,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         context,
                                         comment=get_one_value(class_schema, "comment"))
    return response_dict


def assemble_schema_dict(query_params, normalized_uri, title, predicates, context, **kw):
    effective_context = {"@language": query_params.get("lang")}
    effective_context.update(context.context)

    query_params.resource_url = query_params.base_url
    base_url = remove_last_slash(query_params.base_url)

    href = assemble_url(base_url, {"class_prefix": query_params["class_prefix"]})

    links = [
        {
            'rel': "self",
            'href': "{+_base_url}",
            'method': "GET"
        },
        {
            'rel': "class",
            'href': self_url(query_params),
            'method': "GET"
        }
    ]
    add_link(links, "collection", href.replace('_schema', ''))

    action_links = crud_links(query_params)
    links.extend(action_links)

    schema = {
        "type": "object",
        "id": normalized_uri,
        "@context": effective_context,
        "$schema": "http://json-schema.org/draft-03/schema#",
        "title": title,
        "links": links,
        "properties": predicates
    }
    comment = kw.get("comment", None)
    if comment:
        schema["description"] = comment

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
    return triplestore.query_sparql(query, query_params.triplestore_config)


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
            min_value = binding["min"]["value"]
            if int(min_value):
                current_property[range_].update({"minItems": int(min_value)})
                current_property[range_].update({"required": True})
        elif "max" in binding:
            max_value = binding["max"]["value"]
            if int(max_value):
                current_property[range_].update({"maxItems": int(max_value)})

    return cardinalities


QUERY_CARDINALITIES = """
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
        } .
    }
}"""


def query_cardinalities(query_params):
    query = QUERY_CARDINALITIES % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def query_predicates(query_params):
    response = _query_predicate_with_lang(query_params)

    if not response['results']['bindings']:
        return _query_predicate_without_lang(query_params)
    else:
        return response


QUERY_PREDICATE_WITH_LANG = """
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?range_graph ?range_label ?super_property
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
      FILTER (bound(?range))
    }
    FILTER (!isBlank(?range))
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
    FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
    FILTER(langMatches(lang(?title), "%(lang)s") OR langMatches(lang(?title), "")) .
    OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
    FILTER(langMatches(lang(?predicate_comment), "%(lang)s") OR langMatches(lang(?predicate_comment), "")) .
    OPTIONAL {
      GRAPH ?range_graph {
        ?range rdfs:label ?range_label .
        FILTER(langMatches(lang(?range_label), "%(lang)s") OR langMatches(lang(?range_label), "")) .
      }
    }
}"""


def _query_predicate_with_lang(query_params):
    query_params["filter_classes_clause"] = "FILTER (?domain_class IN (<" + ">, <".join(query_params["superclasses"]) + ">))"

    query = QUERY_PREDICATE_WITH_LANG % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


QUERY_PREDICATE_WITHOUT_LANG = """
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?range_graph ?range_label ?super_property
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
      FILTER (bound(?range))
    }
    FILTER (!isBlank(?range))
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
    FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
    OPTIONAL { GRAPH ?range_graph {  ?range rdfs:label ?range_label . } } .
    OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
}"""


def _query_predicate_without_lang(query_params):
    query_params["filter_classes_clause"] = "FILTER (?domain_class IN (<" + ">, <".join(query_params["superclasses"]) + ">))"
    query = QUERY_PREDICATE_WITHOUT_LANG % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def query_superclasses(query_params):
    result_dict = _query_superclasses(query_params)
    superclasses = filter_values(result_dict, "class")
    return superclasses


QUERY_SUPERCLASS = """
SELECT DISTINCT ?class
WHERE {
    <%(class_uri)s> rdfs:subClassOf ?class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
    ?class a owl:Class .
}
"""


def _query_superclasses(query_params):
    query = QUERY_SUPERCLASS % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def items_from_range(context, range_uri):
    short_range = context.normalize_uri_value(range_uri)
    if short_range == 'xsd:date' or short_range == 'xsd:dateTime':
        return {"type": "string", "format": "date"}
    else:
        return {"type": _MAP_XSD_TO_JSON_TYPE.get(short_range, 'object'), "format": short_range}


def assemble_predicate(predicate_uri, binding_row, cardinalities, context):

    predicate_graph = binding_row["predicate_graph"]['value']
    predicate_type = binding_row['type']['value']

    range_uri = binding_row['range']['value']
    range_graph = binding_row.get('range_graph', {}).get('value', "")
    range_label = binding_row.get('range_label', {}).get('value', "")

    # compression-related
    compressed_range_uri = context.normalize_uri_value(range_uri)
    compressed_range_graph = context.prefix_to_slug(range_graph)
    compressed_graph = context.prefix_to_slug(predicate_graph)

    # build up predicate dictionary
    predicate = {}
    predicate["title"] = binding_row["title"]['value']
    predicate["graph"] = compressed_graph

    if "predicate_comment" in binding_row:
        predicate["description"] = binding_row["predicate_comment"]['value']

    if predicate_type == OBJECT_PROPERTY:
        context.add_object_property(predicate_uri, compressed_range_uri)
        predicate["range"] = {'@id': compressed_range_uri,
                              'graph': compressed_range_graph,
                              'title': range_label,
                              'type': 'string',
                              'format': 'uri'}

        # todo: unittest
        max_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('maxItems', 2)
        min_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('minItems', 2)

        if (min_items > 1) or (max_items > 1) or (not min_items and not max_items):
            predicate["type"] = "array"
            predicate["items"] = {"type": "string", "format": "uri"}
        else:
            predicate["type"] = "string"
            predicate["format"] = "uri"

    elif predicate_type == DATATYPE_PROPERTY:
        # add predicate['type'] and (optional) predicate['format']
        predicate.update(items_from_range(context, range_uri))

    if predicate["type"] == "array":
        if (predicate_uri in cardinalities) and (range_uri in cardinalities[predicate_uri]):
            predicate_restriction = cardinalities[predicate_uri]
            predicate.update(predicate_restriction[range_uri])
    else:
        required = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('required', False)
        if required:
            predicate['required'] = True

    return predicate


def get_common_key(items, key):
    first_key = items[0].get(key, '')
    if all(each_item.get(key) == first_key for each_item in items):
        return first_key
    else:
        return ''


def merge_ranges(one_range, another_range):
    if isinstance(one_range, list) and isinstance(another_range, list):
        one_range.extend(another_range)
    elif isinstance(one_range, list):
        one_range.append(another_range)
    elif isinstance(another_range, list):
        another_range.append(one_range)
        one_range = another_range
    else:
        one_range = [one_range, another_range]

    # no reason for nightmares - the code bellow simply removes duplicates
    one_range = [dict(item) for item in set([tuple(dict_.items()) for dict_ in one_range])]
    return one_range


def normalize_predicate_range(predicate):
    if not 'range' in predicate:
        predicate_range = {}
        predicate_range['type'] = predicate['type']
        if 'format' in predicate:
            predicate_range['format'] = predicate['format']
        predicate['range'] = predicate_range
    return predicate


def join_predicates(old, new):
    old = normalize_predicate_range(old)
    new = normalize_predicate_range(new)

    merged_ranges = merge_ranges(old['range'], new['range'])

    merged_predicate = old
    merged_predicate['range'] = merged_ranges
    merged_predicate['type'] = get_common_key(merged_ranges, 'type')
    merged_predicate['format'] = get_common_key(merged_ranges, 'format')

    return merged_predicate


def convert_bindings_dict(context, bindings, cardinalities):

    super_predicates = get_super_properties(context, bindings)
    assembled_predicates = {}

    for binding_row in bindings:
        predicate_uri = binding_row['predicate']['value']
        predicate_key = context.normalize_uri_key(predicate_uri)
        if not predicate_uri in super_predicates.keys():
            predicate = assemble_predicate(predicate_uri, binding_row, cardinalities, context)
            existing_predicate = assembled_predicates.get(predicate_key, False)
            if existing_predicate:
                if existing_predicate != predicate:
                    assembled_predicates[predicate_key] = join_predicates(existing_predicate, predicate)
            else:
                assembled_predicates[predicate_key] = predicate

    return assembled_predicates
