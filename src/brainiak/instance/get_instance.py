                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    # -*- coding: utf-8 -*-

from brainiak import triplestore, settings
from brainiak.instance.common import extract_class_uri, extract_graph_uri, get_class_and_graph, must_retrieve_graph_and_class_uri
from brainiak.schema import get_class
from brainiak.type_mapper import _MAP_JSON_TO_PYTHON
from brainiak.utils.links import build_class_url, split_prefix_and_id_from_uri
from brainiak.utils.sparql import get_super_properties, is_result_empty, decode_boolean


def get_instance(query_params):
    """
    Given a URI, verify that the type corresponds to the class being passed as a parameter
    Retrieve all properties and objects of this URI (subject)
    """
    if must_retrieve_graph_and_class_uri(query_params):
        query_result_dict = get_class_and_graph(query_params)
        bindings = query_result_dict['results']['bindings']
        query_params["graph_uri"] = extract_graph_uri(bindings)
        query_params["class_uri"] = extract_class_uri(bindings)

    query_result_dict = query_all_properties_and_objects(query_params)

    if is_result_empty(query_result_dict):
        return None
    else:
        query_params["class_schema"] = get_class.get_cached_schema(query_params)
        return assemble_instance_json(query_params,
                                      query_result_dict)


def build_items_dict(bindings, class_uri, expand_object_properties, class_schema):
    super_predicates = get_super_properties(bindings)

    items_dict = {}
    for item in bindings:
        predicate_uri = item["predicate"]["value"]
        object_value = item["object"]["value"]
        object_type = item["object"].get("type")
        object_label = item.get("object_label", {}).get("value")
        if expand_object_properties and object_type == "uri":
            if object_label:
                value = {"@id": object_value, "title": object_label}
            else:
                msg = u"The predicate {0} refers to an object {1} which doesn't have a label.".format(predicate_uri, object_value) + \
                    " Set expand_object_properties=0 if you don't care about this ontological inconsistency."
                raise Exception(msg)
        else:
            value = _convert_to_python(object_value, class_schema, predicate_uri)

        if predicate_uri in items_dict:
            if not isinstance(items_dict[predicate_uri], list):
                value_list = [items_dict[predicate_uri]]
            else:
                value_list = items_dict[predicate_uri]
            value_list.append(value)
            items_dict[predicate_uri] = value_list
        else:
            base_uri = None
            if predicate_uri in class_schema["properties"]:
                base_uri = predicate_uri

            # Here we IGNORE predicate/object values that exist in the triplestore
            #  but the predicate is not in the class schema
            if base_uri:
                if class_schema["properties"][base_uri][u'type'] == u'array':
                    items_dict[predicate_uri] = [value]
                else:
                    items_dict[predicate_uri] = value

    remove_super_properties(items_dict, super_predicates)

    if not class_uri is None:
        items_dict["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"] = class_uri

    return items_dict


def remove_super_properties(items_dict, super_predicates):
    for (analyzed_predicate, value) in items_dict.items():
        if analyzed_predicate in super_predicates.keys():
            sub_predicate = super_predicates[analyzed_predicate]
            if sub_predicate in items_dict:
                sub_value = items_dict[sub_predicate]
                if value == sub_value or (sub_value in value):
                    items_dict.pop(analyzed_predicate)


def check_and_clean_rdftype(instance_type, items):
    """Validate actual type and remove rdf:type from the instance to be returned"""
    if 'rdf:type' in items:
        rdftype = 'rdf:type'
    elif 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in items:
        rdftype = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    else:
        rdftype = None
    if rdftype is not None:
        msg = u"The type specified={0} is not the same informed from the triplestore={1}"
        if instance_type != items[rdftype]:
            raise Exception(msg.format(instance_type, items[rdftype]))
        del items[rdftype]


def assemble_instance_json(query_params, query_result_dict):

    expand_object_properties = query_params.get("expand_object_properties") == "1"
    include_meta_properties = query_params.get("meta_properties") is None or query_params.get("meta_properties") == "1"
    items = build_items_dict(query_result_dict['results']['bindings'],
                             query_params["class_uri"],
                             expand_object_properties,
                             query_params["class_schema"])

    if include_meta_properties:
        class_url = build_class_url(query_params)
        query_params.resource_url = u"{0}/{1}".format(class_url, query_params['instance_id'])
        response = split_prefix_and_id_from_uri(query_params['instance_uri'])
        instance_uri = query_params['instance_uri']
        instance_prefix, instance_id = split_prefix_and_id_from_uri(instance_uri)
        instance = {
            "_base_url": query_params.base_url,
            "_instance_prefix": instance_prefix,
            "_resource_id": instance_id,
            "@id": instance_uri,
            "@type": query_params["class_uri"]
        }

        check_and_clean_rdftype(instance['@type'], items)
    else:
        instance = {}

    instance.update(items)
    return instance


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE = u"""
DEFINE input:inference <%(ruleset)s>
SELECT DISTINCT ?predicate ?object %(object_label_variable)s ?super_property {
    <%(instance_uri)s> a <%(class_uri)s> ;
    ?predicate ?object .
OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
%(object_label_optional_clause)s
FILTER((langMatches(lang(?object), "%(lang)s") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
}
"""


def query_all_properties_and_objects(query_params):
    query_params["ruleset"] = settings.DEFAULT_RULESET_URI
    expand_object_properties = query_params.get("expand_object_properties") == "1"
    if expand_object_properties:
        query_params["object_label_variable"] = "?object_label"
        query_params["object_label_optional_clause"] = "OPTIONAL { ?object rdfs:label ?object_label } ."
    else:
        query_params["object_label_variable"] = ""
        query_params["object_label_optional_clause"] = ""
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE_BY_URI = u"""
DEFINE input:inference <%(ruleset)s>
SELECT DISTINCT ?predicate ?object %(object_label_variable)s ?super_property ?class_uri ?graph_uri {
    GRAPH ?graph_uri { <%(instance_uri)s> a ?class_uri } .
    <%(instance_uri)s> ?predicate ?object .
OPTIONAL { ?predicate rdfs:subPropertyOf ?super_property } .
%(object_label_optional_clause)s
FILTER((langMatches(lang(?object), "%(lang)s") OR langMatches(lang(?object), "")) OR (IsURI(?object))) .
}
"""


def query_all_properties_and_objects_by_instance_uri(query_params):
    query_params["ruleset"] = settings.DEFAULT_RULESET_URI
    expand_object_properties = query_params.get("expand_object_properties") == "1"
    if expand_object_properties:
        query_params["object_label_variable"] = "?object_label"
        query_params["object_label_optional_clause"] = "OPTIONAL { ?object rdfs:label ?object_label } ."
    else:
        query_params["object_label_variable"] = ""
        query_params["object_label_optional_clause"] = ""
    query = QUERY_ALL_PROPERTIES_AND_OBJECTS_TEMPLATE_BY_URI % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def _convert_to_python(object_value, class_schema, predicate_uri):
    if predicate_uri in class_schema["properties"]:
        if class_schema["properties"][predicate_uri]['type'] == "array":
            schema_type = class_schema["properties"][predicate_uri]['items']['type']
        else:
            schema_type = class_schema["properties"][predicate_uri]['type']

        python_type = _MAP_JSON_TO_PYTHON[schema_type]
        if python_type == bool:
            converted_value = decode_boolean(object_value)
        else:
            # TODO: unittest
            msg = u"The property {0} is mapped to a inconsistent value {1}".format(predicate_uri, object_value)
            try:
                converted_value = python_type(object_value)
            except ValueError:
                raise Exception(msg)

        return converted_value
    else:  # values with predicate_uri not in schema will be ignored anyway
        return object_value
