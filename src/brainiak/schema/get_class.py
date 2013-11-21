# -*- coding: utf-8 -*-

from brainiak import triplestore
from brainiak.log import get_logger
from brainiak.prefixes import MemorizeContext
from brainiak.type_mapper import DATATYPE_PROPERTY, OBJECT_PROPERTY, _MAP_EXPAND_XSD_TO_JSON_TYPE
from brainiak.utils.i18n import _
from brainiak.utils.cache import build_key_for_class, memoize
from brainiak.utils.links import assemble_url, add_link, self_url, crud_links, remove_last_slash
from brainiak.utils.resources import LazyObject
from brainiak.utils.sparql import add_language_support, filter_values, get_one_value, get_super_properties, InstanceError, bindings_to_dict

logger = LazyObject(get_logger)


class SchemaNotFound(Exception):
    pass


def get_cached_schema(query_params, include_meta=False):
    schema_key = build_key_for_class(query_params)
    class_object = memoize(query_params, get_schema, query_params, key=schema_key)
    if not class_object["body"]:
        msg = _(u"The class definition for {0} was not found in graph {1}")
        raise SchemaNotFound(msg.format(query_params['class_uri'], query_params['graph_uri']))
    if include_meta:
        return class_object
    else:
        return class_object['body']


def get_schema(query_params):
    context = MemorizeContext(normalize_uri=query_params['expand_uri'])
    class_schema = query_class_schema(query_params)
    if not class_schema["results"]["bindings"]:
        return
    query_params["superclasses"] = query_superclasses(query_params)
    predicates_and_cardinalities = get_predicates_and_cardinalities(context, query_params)
    response_dict = assemble_schema_dict(query_params,
                                         get_one_value(class_schema, "title"),
                                         predicates_and_cardinalities,
                                         context,
                                         comment=get_one_value(class_schema, "comment"))
    return response_dict


def assemble_schema_dict(query_params, title, predicates, context, **kw):
    effective_context = {"@language": query_params.get("lang")}
    effective_context.update(context.context)

    query_params.resource_url = query_params.base_url
    base_url = remove_last_slash(query_params.base_url)

    href = assemble_url(base_url, {"class_prefix": query_params.get("class_prefix", "")})

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
        },
        {
            "href": href.replace('_schema', ''),
            "method": "POST",
            "rel": "create",
            "schema": {"$ref": "{+_base_url}"}
        }
    ]
    add_link(links, "collection", href.replace('_schema', ''))

    action_links = crud_links(query_params)
    links.extend(action_links)

    schema = {
        "type": "object",
        "id": query_params["class_uri"],
        "@context": effective_context,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": title,
        "links": links,
        "properties": predicates
    }
    comment = kw.get("comment", None)
    if comment:
        schema["description"] = comment
    return schema


QUERY_CLASS_SCHEMA = u"""
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

    bindings = query_predicates(query_params)
    predicate_dict = bindings_to_dict('predicate', bindings)

    try:
        cardinalities = _extract_cardinalities(query_result['results']['bindings'], predicate_dict)
    except InstanceError as ex:
        msg = _(u"{0} for class {1}").format(ex.message, query_params.get('class_uri', ''))
        raise InstanceError(msg)

    return convert_bindings_dict(context,
                                 bindings['results']['bindings'],
                                 cardinalities,
                                 query_params['superclasses'])


def _extract_cardinalities(bindings, predicate_dict):
    cardinalities = {}
    for binding in bindings:
        property_ = binding["predicate"]["value"]
        try:
            range_ = binding["range"]["value"]
        except KeyError:
            try:
                range_ = predicate_dict[property_]["range"]["value"]
            except KeyError:
                msg = _(u"The property {0} is not defined properly").format(property_)
                raise InstanceError(msg)

        if not property_ in cardinalities:
            cardinalities[property_] = {}

        if not range_ in cardinalities[property_] and not range_.startswith("nodeID://"):
            cardinalities[property_][range_] = {}

        current_property = cardinalities[property_]

        if "min" in binding:
            min_value = binding["min"]["value"]
            try:
                min_value = int(min_value)
            except ValueError:
                msg = _(u"The property {0} defines a non-integer owl:minQualifiedCardinality {1}").format(property_, min_value)
                raise InstanceError(msg)
            else:
                current_property[range_].update({"minItems": min_value})
                if min_value:
                    current_property[range_].update({"required": True})

        if "max" in binding:
            max_value = binding["max"]["value"]
            try:
                max_value = int(max_value)
            except ValueError:
                msg = _(u"The property {0} defines a non-integer owl:maxQualifiedCardinality {1}").format(property_, max_value)
                raise InstanceError(msg)
            else:
                current_property[range_].update({"maxItems": max_value})

    return cardinalities


QUERY_CARDINALITIES = u"""
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
        response = _query_predicate_without_lang(query_params)

    return response

QUERY_PREDICATE_WITH_LANG = u"""
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?range_graph ?range_label ?super_property ?domain_class ?unique_value
WHERE {
    {
      GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
    } UNION {
      GRAPH ?predicate_graph {?predicate rdfs:domain ?blank} .
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
      FILTER (BOUND(?range))
    }
    FILTER (!isBlank(?range))
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
    OPTIONAL { ?predicate base:tem_valor_unico ?unique_value } .
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


QUERY_PREDICATE_WITHOUT_LANG = u"""
SELECT DISTINCT ?predicate ?predicate_graph ?predicate_comment ?type ?range ?title ?range_graph ?range_label ?super_property ?domain_class ?unique_value
WHERE {
    {
      GRAPH ?predicate_graph { ?predicate rdfs:domain ?domain_class  } .
    } UNION {
      GRAPH ?predicate_graph {?predicate rdfs:domain ?blank} .
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
      FILTER (BOUND(?range))
    }
    FILTER (!isBlank(?range))
    ?predicate rdfs:label ?title .
    ?predicate rdf:type ?type .
    OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
    OPTIONAL { ?predicate base:tem_valor_unico ?unique_value } .
    FILTER (?type in (owl:ObjectProperty, owl:DatatypeProperty)) .
    OPTIONAL { GRAPH ?range_graph {  ?range rdfs:label ?range_label . } } .
    OPTIONAL { ?predicate rdfs:comment ?predicate_comment }
}"""


def _query_predicate_without_lang(query_params):
    query_params["filter_classes_clause"] = u"FILTER (?domain_class IN (<" + u">, <".join(query_params["superclasses"]) + u">))"
    query = QUERY_PREDICATE_WITHOUT_LANG % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def query_superclasses(query_params):
    result_dict = _query_superclasses(query_params)
    superclasses = filter_values(result_dict, "class")
    return superclasses


QUERY_SUPERCLASS = u"""
SELECT DISTINCT ?class
WHERE {
    <%(class_uri)s> rdfs:subClassOf ?class OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0)) .
    ?class a owl:Class .
}
"""


def _query_superclasses(query_params):
    query = QUERY_SUPERCLASS % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def items_from_range(range_uri, min_items=1, max_items=1):
    # Compute first a dict that will either be used as the root type or the item type of an array
    if range_uri == 'http://www.w3.org/2001/XMLSchema#date' or range_uri == 'http://www.w3.org/2001/XMLSchema#dateTime':
        nested_predicate = {"type": "string", "format": "date"}
    else:
        mapped_type = _MAP_EXPAND_XSD_TO_JSON_TYPE.get(range_uri, None)
        if mapped_type:
            nested_predicate = {"type": mapped_type}
        else:
            logger.error(_(u"Range URI {0} not mapped to JSON type.").format(range_uri))
            nested_predicate = {"type": "string"}

    # decide if thtis is an array or a scalar type
    if (min_items > 1) or (max_items > 1) or (not min_items and not max_items):
        predicate = {
            "type": "array",
            "items": nested_predicate
        }
    else:
        predicate = nested_predicate

    predicate["datatype"] = range_uri
    return predicate


def assemble_predicate(predicate_uri, binding_row, cardinalities, context):
    predicate_graph = binding_row["predicate_graph"]['value']
    predicate_type = binding_row['type']['value']

    range_uri = binding_row['range']['value']
    range_graph = binding_row.get('range_graph', {}).get('value', "")
    range_label = binding_row.get('range_label', {}).get('value', "")
    class_uri = binding_row["domain_class"]['value']

    # build up predicate dictionary
    predicate = {
        "class": class_uri,
        "graph": predicate_graph,
        "title": binding_row["title"]['value']
    }

    if "predicate_comment" in binding_row:
        predicate["description"] = binding_row["predicate_comment"]['value']

    if predicate_type == OBJECT_PROPERTY:
        context.add_object_property(predicate_uri, range_uri)
        predicate["range"] = {'@id': range_uri,
                              'graph': range_graph,
                              'title': range_label,
                              'type': 'string',
                              'format': 'uri'}

        max_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('maxItems', 2)
        min_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('minItems', 2)

        if (min_items > 1) or (max_items > 1) or (not min_items and not max_items):
            predicate["type"] = "array"
            predicate["items"] = {"type": "string", "format": "uri"}
        else:
            predicate["type"] = "string"
            predicate["format"] = "uri"

    elif predicate_type == DATATYPE_PROPERTY:
        max_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('maxItems', 1)
        min_items = cardinalities.get(predicate_uri, {}).get(range_uri, {}).get('minItems', 1)
        # add predicate['type'] and (optional) predicate['format']
        predicate.update(items_from_range(range_uri, min_items, max_items))

    else:  # TODO: owl:AnnotationProperty
        msg = _(u"Predicates of type {0} are not supported yet").format(predicate_type)
        raise InstanceError(msg)

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
        predicate['items'] = predicate_range
    return predicate


def join_predicates(old, new):
    old = normalize_predicate_range(old)
    new = normalize_predicate_range(new)

    merged_ranges = merge_ranges(old['range'], new['range'])

    merged_predicate = old
    merged_predicate['range'] = merged_ranges

    old_max_items = old.get('maxItems', 2)
    old_min_items = old.get('minItems', 2)
    new_max_items = new.get('maxItems', 2)
    new_min_items = new.get('minItems', 2)

    if (old_min_items > 1) or (old_max_items > 1) or (not old_min_items and not old_max_items) or \
            (new_min_items > 1) or (new_max_items > 1) or (not new_min_items and not new_max_items):
        merged_predicate["type"] = "array"
        merged_items = {}
        merged_items.update(old.get('items', {}))
        merged_items.update(new.get('items', {}))
        merged_predicate["items"] = merged_items
    else:
        merged_predicate['type'] = get_common_key(merged_ranges, 'type')
        merged_predicate['format'] = get_common_key(merged_ranges, 'format')
        merged_predicate.pop("items", None)
    return merged_predicate


def most_specialized_predicate(class_hierarchy, predicate_a, predicate_b):
    index_a = class_hierarchy.index(predicate_a['class'])
    index_b = class_hierarchy.index(predicate_b['class'])
    return predicate_a if index_a < index_b else predicate_b


def convert_bindings_dict(context, bindings, cardinalities, superclasses):

    super_predicates = get_super_properties(bindings)
    assembled_predicates = {}

    for binding_row in bindings:
        predicate_uri = binding_row['predicate']['value']

        # super_predicate is when we use rdfs:subPropertyOf
        # this case does not consider inherited predicates
        if predicate_uri in super_predicates.keys():
            continue

        predicate = assemble_predicate(predicate_uri, binding_row, cardinalities, context)
        existing_predicate = assembled_predicates.get(predicate_uri, False)
        if existing_predicate:
            if 'datatype' in existing_predicate and 'datatype' in predicate:
                assembled_predicates[predicate_uri] = most_specialized_predicate(superclasses,
                                                                                 existing_predicate,
                                                                                 predicate)
            elif existing_predicate != predicate:
                assembled_predicates[predicate_uri] = join_predicates(existing_predicate, predicate)

            else:
                msg = _(u"The property {0} seems to be duplicated in class {1}")
                raise InstanceError(msg.format(predicate_uri, predicate["class"]))

        else:
            assembled_predicates[predicate_uri] = predicate

        if "unique_value" in binding_row and binding_row["unique_value"]["value"] == "1":
            assembled_predicates[predicate_uri]["unique_value"] = True

    return assembled_predicates
