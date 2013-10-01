from tornado.web import HTTPError

from brainiak import settings, triplestore
from brainiak.prefixes import uri_to_slug
from brainiak.search_engine import run_search
from brainiak.utils.sparql import add_language_support, compress_keys_and_values, filter_values, is_result_empty
from brainiak.utils.resources import calculate_offset, decorate_dict_with_pagination

RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"

SUGGEST_PARAM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Describe the parameters given to the suggest primitive",
    "type": "object",
    "required": ["search"],
    "additionalProperties": False,
    "properties": {
        "search": {
            "type": "object",
            "required": ["pattern", "target"],
            "additionalProperties": False,
            "properties": {
                "pattern": {"type": "string"},
                "target": {"type": "string", "format": "uri"},
                "graphs": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },
                "classes": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },

            }
        },
        "response": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "required_fields": {
                    "type": "boolean"
                },
                "class_fields": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },
                "classes": {
                    "type": "array",
                    "uniqueItems": True,
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["@type", "instance_fields"],
                        "additionalProperties": False,
                        "properties": {
                            "@type": {"type": "string", "format": "uri"},
                            "instance_fields": {
                                "type": "array",
                                "items": {"type": "string", "format": "uri"},
                                "minItems": 1,
                                "uniqueItems": True
                            }
                        }
                    },
                },
                "instance_fields": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },
                "meta_fields": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"},
                    "minItems": 1,
                    "uniqueItems": True
                },
            }
        }

    }
}


def do_suggest(query_params, suggest_params):
    search_params = suggest_params["search"]
    response_params = suggest_params.get("response", {})

    range_result = _get_predicate_ranges(query_params, search_params)
    if is_result_empty(range_result):
        message = "Either the predicate {0} does not exists or it does not have" + \
            " any rdfs:range defined in the triplestore"
        message = message.format(search_params["target"])
        raise HTTPError(400, message)

    classes = _validate_class_restriction(query_params, range_result)
    graphs = _validate_graph_restriction(query_params, range_result)
    indexes = ["semantica." + uri_to_slug(graph) for graph in graphs]

    compressed_result = compress_keys_and_values(range_result)
    class_label_dict, class_graph_dict = _build_class_label_and_class_graph_dicts(compressed_result)

    title_fields = [RDFS_LABEL]
    title_fields += _get_subproperties(query_params, RDFS_LABEL)
    search_fields = list(set(_get_search_fields(query_params, suggest_params) + title_fields))

    response_fields, response_fields_by_class, required_fields = _get_response_fields(
        query_params, response_params, classes, class_graph_dict, title_fields)

    request_body = _build_body_query(query_params, search_params, classes,
                                     search_fields, response_fields)
    elasticsearch_result = run_search(request_body, indexes=indexes)

    class_fields = response_params.get("class_fields", [])

    items, item_count = _build_items(query_params, elasticsearch_result, class_label_dict,
                                     title_fields, response_fields_by_class,
                                     class_fields, required_fields)
    if not items:
        return {}
    else:
        return build_json(items, item_count, query_params)


def build_json(items_list, item_count, query_params):

    json = {
        '_base_url': query_params.base_url,
        'items': items_list,
        "@context": {"@language": query_params.get("lang")},
    }

    calculate_total_items = lambda: item_count
    decorate_dict_with_pagination(json, query_params, calculate_total_items)

    return json


QUERY_PREDICATE_RANGES = """
SELECT DISTINCT ?range ?range_label ?range_graph {
  {
    <%(target)s> rdfs:range ?root_range .
  }
  UNION {
    <%(target)s> rdfs:range ?blank .
    ?blank a owl:Class .
    ?blank owl:unionOf ?enumeration .
    OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
    OPTIONAL { ?list_node rdf:first ?root_range } .
  }
  FILTER (!isBlank(?root_range))
  ?range rdfs:subClassOf ?root_range OPTION(TRANSITIVE, t_min (0)) .
  ?range rdfs:label ?range_label .
  GRAPH ?range_graph { ?range a owl:Class } .
  %(lang_filter_range_label)s
}
"""


def _build_predicate_ranges_query(query_params, search_params):
    (params, language_tag) = add_language_support(query_params, "range_label")
    params.update(search_params)
    return QUERY_PREDICATE_RANGES % params


def _get_predicate_ranges(query_params, search_params):
    query = _build_predicate_ranges_query(query_params, search_params)
    return triplestore.query_sparql(query, query_params.triplestore_config)


QUERY_SUBPROPERTIES = """
DEFINE input:inference <http://semantica.globo.com/ruleset>
SELECT DISTINCT ?property WHERE {
  ?property rdfs:subPropertyOf <%s>
}
"""


def _get_subproperties(params, super_property):
    query = QUERY_SUBPROPERTIES % super_property
    result = triplestore.query_sparql(query, params.triplestore_config)
    return filter_values(result, "property")


def _get_search_fields(query_params, search_params):
    search_fields_in_search_params = search_params.get("fields", [])
    search_fields = set(search_fields_in_search_params)
    for field in search_fields_in_search_params:
        sub_properties = _get_subproperties(query_params, field)
        search_fields.update(sub_properties)

    return list(search_fields)


def _validate_class_restriction(search_params, range_result):
    classes = set(filter_values(range_result, "range"))
    if "classes" in search_params:
        classes_not_in_range = list(set(search_params["classes"]).difference(classes))
        if classes_not_in_range:
            raise HTTPError(400,
                            "Classes {0} are not in the range of predicate '{1}'".format(classes_not_in_range, search_params["target"]))
        classes = search_params["classes"]

    return list(classes)


def _validate_graph_restriction(search_params, range_result):
    graphs = set(filter_values(range_result, "range_graph"))
    if "graphs" in search_params:
        graphs_set = set(search_params["graphs"])
        graphs_not_in_range = list(graphs_set.difference(graphs))
        if graphs_not_in_range:
            raise HTTPError(400,
                            "Classes in the range of predicate '{0}' are not in graphs {1}".format(search_params["target"], graphs_not_in_range))
        graphs = graphs_set

    graphs = graphs.difference(set(settings.GRAPHS_WITHOUT_INSTANCES))

    if not graphs:
        raise HTTPError(400,
                        "Classes in the range of predicate '{0}' are in graphs without instances, such as: {1}".format(
                            search_params["target"], settings.GRAPHS_WITHOUT_INSTANCES))
    return list(graphs)


QUERY_CLASS_FIELDS = """
SELECT DISTINCT ?field_value {
  ?s <%(field)s> ?field_value
  %(filter_clause)s
}
"""


def _build_class_fields_query(classes, field):
    conditions = ["?s = <{0}>".format(klass) for klass in classes]
    conditions = " OR ".join(conditions)
    filter_clause = "FILTER(" + conditions + ")"
    query = QUERY_CLASS_FIELDS % {
        "field": field,
        "filter_clause": filter_clause
    }
    return query


def _get_class_fields_value(query_params, classes, meta_field):
    query = _build_class_fields_query(classes, meta_field)
    class_field_query_response = triplestore.query_sparql(query, query_params.triplestore_config)
    class_field_values = filter_values(class_field_query_response, "field_value")
    return class_field_values


def _get_response_fields(query_params, response_params, classes, class_graph_dict, title_fields):
    response_fields = set([])
    response_fields_by_class = {}

    response_fields.update(title_fields)

    if "required_fields" not in response_params or response_params["required_fields"]:
        required_fields = _get_required_fields(query_params, response_params, classes, class_graph_dict)
        response_fields.update(required_fields)
    else:
        required_fields = []

    meta_fields = _get_response_fields_from_meta_fields(query_params, response_params, classes)
    response_fields.update(meta_fields)

    instance_fields = set(response_params.get("instance_fields", []))
    response_fields.update(instance_fields)

    classes_dict = response_params.get("classes", [])
    response_fields_by_class, fields_by_class_set = _get_response_fields_from_classes_dict(
        classes_dict, response_fields, classes)
    response_fields.update(fields_by_class_set)

    response_fields = list(response_fields)

    return response_fields, response_fields_by_class, required_fields


def _get_required_fields(query_params, response_params, classes, class_graph_dict):
    from brainiak.schema.get_class import get_cached_schema
    required_fields = set([])

    for klass in classes:
        query_params["class_uri"] = klass
        query_params["graph_uri"] = class_graph_dict[klass]
        schema = get_cached_schema(query_params)
        required_from_class = _get_required_fields_from_schema_response(schema)
        required_fields.update(required_from_class)

    return required_fields


def _get_required_fields_from_schema_response(schema):
    required_fields = []
    for prop in schema["properties"]:
        if "required" in schema["properties"][prop] and schema["properties"][prop]["required"]:
            required_fields.append(prop)

    return required_fields


def _get_response_fields_from_meta_fields(query_params, response_params, classes):
    meta_fields_response = set([])
    for meta_field in response_params.get("meta_fields", []):
        meta_field_values = _get_class_fields_value(query_params, classes, meta_field)
        for meta_field_value in meta_field_values:
            values = meta_field_value.split(",")
            values = [v.strip() for v in values]
            meta_fields_response.update(values)

    return meta_fields_response


def _get_response_fields_from_classes_dict(fields_by_class_list, response_fields, classes):
    response_fields_by_class = dict.fromkeys(classes, list(response_fields))
    fields_by_class_set = set([])
    for fields_by_class in fields_by_class_list:
        klass = fields_by_class["@type"]
        specific_class_fields = fields_by_class["instance_fields"]

        actual_fields = set(response_fields_by_class.get(klass, []))
        actual_fields.update(set(specific_class_fields))
        response_fields_by_class[klass] = list(actual_fields)
        fields_by_class_set.update(set(specific_class_fields))

    return response_fields_by_class, fields_by_class_set


def _build_body_query(query_params, search_params, classes, search_fields, response_fields):
    patterns = search_params["pattern"].lower().split()
    query_string = " AND ".join(patterns) + "*"
    body = {
        "from": int(calculate_offset(query_params)),
        "size": int(query_params.get("per_page", settings.DEFAULT_PER_PAGE)),
        "fields": response_fields,
        "query": {
            "query_string": {
                "query": query_string,
                "fields": search_fields
            }
        },
        "filter": _build_type_filters(classes)
    }

    return body


def _build_type_filters(classes):
    filter_list = []
    for klass in classes:
        filter_dict = {"type": {"value": klass}}
        filter_list.append(filter_dict)

    type_filters = {
        "or": filter_list
    }
    return type_filters


def _build_class_label_and_class_graph_dicts(compressed_result):
    class_label_dict = {}
    class_graph_dict = {}
    for result in compressed_result:
        class_label_dict[result["range"]] = result["range_label"]
        class_graph_dict[result["range"]] = result["range_graph"]
    return class_label_dict, class_graph_dict


def _get_title_value(elasticsearch_fields, title_fields):
    for field in reversed(title_fields):
        title = elasticsearch_fields.get(field)
        if title:
            return (field, title)
    raise RuntimeError("No title fields in search engine")


QUERY_PREDICATE_VALUES = """
SELECT ?object_value ?object_value_label ?predicate ?predicate_title {
  <%(instance_uri)s> ?predicate ?object_value OPTION(inference "http://semantica.globo.com/ruleset") .
  OPTIONAL { ?object_value rdfs:label ?object_value_label OPTION(inference "http://semantica.globo.com/ruleset") }
  ?predicate rdfs:label ?predicate_title .
  %(filter_clause)s
}
"""


def _build_predicate_values_query(instance_uri, predicates):
    conditions = ["?predicate = <{0}>".format(predicate) for predicate in predicates]
    conditions = " OR ".join(conditions)
    filter_clause = "FILTER(" + conditions + ")"
    query = QUERY_PREDICATE_VALUES % {
        "instance_uri": instance_uri,
        "filter_clause": filter_clause
    }
    return query


def _get_predicate_values(query_params, instance_uri, predicates):
    query = _build_predicate_values_query(instance_uri, predicates)
    query_response = triplestore.query_sparql(query, query_params.triplestore_config)
    return compress_keys_and_values(query_response)


def _get_instance_fields(query_params, instance_uri, klass, title_field, fields_by_class_dict, required_fields):

    instance_fields = {}

    predicates = fields_by_class_dict.get(klass, [])

    if predicates and title_field in predicates:  # title_field is already in response
        predicates.remove(title_field)

    if not predicates:
        return instance_fields

    predicate_values = _get_predicate_values(query_params, instance_uri, predicates)

    if not predicate_values:
        return instance_fields
    else:
        instance_fields_list = []
        for value in predicate_values:
            instance_field_dict = {
                "predicate_id": value["predicate"],
                "predicate_title": value["predicate_title"],
            }
            if value["predicate"] in required_fields:
                instance_field_dict["required"] = True
            else:
                instance_field_dict["required"] = False

            if "object_value_label" in value:
                instance_field_dict["object_id"] = value["object_value"]
                instance_field_dict["object_title"] = value["object_value_label"]
            else:
                instance_field_dict["object_title"] = value["object_value"]


            instance_fields_list.append(instance_field_dict)
        instance_fields["instance_fields"] = instance_fields_list

    return instance_fields


def _get_class_fields_to_response(query_params, classes, class_fields):
    class_fields_to_return = {}
    for field in class_fields:
        field_value = _get_class_fields_value(query_params, classes, field)
        if field_value:
            # Assuming there is only one value to a class_field (annotation property)
            class_fields_to_return[field] = field_value[0]
    if class_fields_to_return:
        return {"class_fields": class_fields_to_return}
    else:
        return class_fields_to_return


def _build_items(query_params, result, class_label_dict,
                 title_fields, fields_by_class_dict,
                 class_fields, required_fields):
    items = []
    item_count = result["hits"]["total"]
    if item_count:
        for item in result["hits"]["hits"]:
            instance_uri = item["_id"]
            title_field, title_value = _get_title_value(item["fields"], title_fields)
            klass = item["_type"]
            item_dict = {
                "@id": instance_uri,
                "title": title_value,
                "@type": klass,
                "type_title": class_label_dict[klass]
            }
            instance_fields = _get_instance_fields(query_params, instance_uri, klass,
                                                   title_field, fields_by_class_dict,
                                                   required_fields)
            item_dict.update(instance_fields)

            class_fields_to_response = _get_class_fields_to_response(query_params, [klass], class_fields)
            item_dict.update(class_fields_to_response)
            items.append(item_dict)

    return items, item_count
