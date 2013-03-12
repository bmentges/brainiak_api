# coding: utf-8
from brainiak.prefixes import shorten_uri
from brainiak.type_mapper import items_from_type, OBJECT_PROPERTY, DATATYPE_PROPERTY, items_from_range


def get_one_value(result_dict, key):
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def filter_values(result_dict, key):
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def compress_keys_and_values(result_dict):
    result_list = []
    for item in result_dict['results']['bindings']:
        row = {}
        for key in item:
            row[key] = item[key]['value']
        result_list.append(row)
    return result_list


def is_result_empty(result_dict):
    return len(result_dict['results']['bindings']) == 0


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


def convert_bindings_dict(context, bindings, cardinalities=None):
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
