import inspect
from urllib import unquote

from tornado.web import HTTPError

from brainiak import settings, triplestore
from brainiak.prefixes import shorten_uri
from brainiak.schema import get_class
from brainiak.type_mapper import MAP_RDF_EXPANDED_TYPE_TO_PYTHON as rdf_to_type
from brainiak.utils.links import build_schema_url_for_instance, remove_last_slash, build_class_url
from brainiak.utils.resources import decorate_with_resource_id, decorate_dict_with_pagination, calculate_offset
from brainiak.utils.sparql import compress_keys_and_values, is_literal, is_url, normalize_term, get_one_value, \
        extract_po_tuples, is_result_true


EXPANDED_RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
SHORTEN_RDFS_LABEL = "rdfs:label"
RDFS_LABEL = [EXPANDED_RDFS_LABEL, SHORTEN_RDFS_LABEL]


class Query(object):
    """
    Creates a SPARQL query for listing instances, provided
    obligatory parameters.

    Usage:

    >>> params = {...}
    >>> sparql_query = Query(params).to_string()

    Obligatory params' keys (provided while creating object):
        class_uri
        graph_uri
        lang
        p
        o
        per_page
        page
        sort_by
        sort_order
    """

    skeleton = u"""
        SELECT DISTINCT %(variables)s
        WHERE {
            %(triples)s
            %(filter)s
        }
        %(sortby)s
        LIMIT %(per_page)s
        OFFSET %(offset)s
    """

    skeleton_count = u"""
        SELECT count(DISTINCT ?subject) as ?total
        WHERE {
            %(triples)s
            %(filter)s
        }
    """

    def __init__(self, params):
        self.params = params

    def should_add_predicate_and_object(self, predicate, object_):
        predicate = shorten_uri(predicate) if not predicate.startswith("?") else predicate

        generic_po = predicate.startswith("?") and object_.startswith("?")
        rdfs_repetition = (predicate in RDFS_LABEL) and object_.startswith("?")

        return not generic_po and not rdfs_repetition

    @property
    def inference_graph(self):
        return settings.DEFAULT_RULESET_URI

    @property
    def po_tuples(self):
        return extract_po_tuples(self.params)

    def next_variable(self, index):
        return u"?literal{0}".format(index)

    @property
    def triples(self):
        tuples = [
            ("<{0}>".format(EXPANDED_RDFS_LABEL), "?label")
        ]
        variable_index = 0
        for predicate, object_, index in self.po_tuples:
            if self.should_add_predicate_and_object(predicate, object_):
                predicate = normalize_term(predicate, self.params["lang"])
                if is_literal(object_) or is_url(object_):
                    # this is used to escape the datatype when filtering objects that are literals
                    variable_index += 1
                    variable_name = self.next_variable(variable_index)
                    tuples.append((predicate, variable_name))
                else:
                    if not is_url(object_):
                        object_ = normalize_term(object_, self.params["lang"])
                        tuples.append((predicate, object_))

        sort_object = self.get_sort_variable()
        sort_sufix = u""
        if sort_object == "?sort_object":
            sort_predicate = normalize_term(self.params["sort_by"])
            if self.params["sort_include_empty"] == "1":
                sort_sufix = u"OPTIONAL {?subject %s ?sort_object}" % sort_predicate
            else:
                tuples.append((sort_predicate, sort_object))

        if self.direct_instances:
            first_statement = u"?subject a <%(class_uri)s> ;\n"
        else:
            tuples.insert(0, ("a", "<%(class_uri)s>"))
            first_statement = "?subject "

        inference = u'OPTION(inference "%s")' % self.inference_graph
        tuples_strings = [u"%s %s %s" % (p, o, inference) for p, o in tuples]

        statement = first_statement + u" ;\n".join(tuples_strings) + u" .\n" + sort_sufix
        statements = statement % self.params

        return u'GRAPH <%(graph_uri)s> { %(statements)s }' % {"statements": statements, 'graph_uri': self.params['graph_uri']}

    @property
    def direct_instances(self):
        return self.params.get("direct_instances_only") == "1"

    @property
    def filter(self):
        translatables = ["?label"]
        statement = ""
        filter_list = []

        # the block bellow is similar to part of variable's method
        # it is "copied" to assure independency between the methods
        # this is used to escape the datatype when filtering objects that are literals
        variable_index = 0
        for predicate, object_, index in self.po_tuples:
            if is_literal(object_) or is_url(object_):
                variable_index += 1
                variable_name = self.next_variable(variable_index)
                literal_filter = u'FILTER(str({0}) = "{1}") .'.format(variable_name, object_)
                if literal_filter not in filter_list:
                    filter_list.append(literal_filter)

        FILTER_CLAUSE = u'FILTER(langMatches(lang(%(variable)s), "%(lang)s") OR langMatches(lang(%(variable)s), "")) .'
        if self.params["lang"]:
            for variable in translatables:
                statement = FILTER_CLAUSE % {
                    "variable": variable,
                    "lang": self.params["lang"]
                }
                filter_list.append(statement)

        if filter_list:
            statement = "\n".join(filter_list)

        return statement

    @property
    def offset(self):
        return calculate_offset(self.params)

    def get_sort_variable(self):
        sort_predicate = self.params["sort_by"]
        sort_label = ""
        if sort_predicate:
            sort_predicate = shorten_uri(sort_predicate) if not sort_predicate.startswith("?") else sort_predicate
            if (sort_predicate in RDFS_LABEL):
                sort_label = "?label"
            else:
                for predicate, object_, index in self.po_tuples:
                    if (sort_predicate == predicate) and object_.startswith("?"):
                        sort_label = object_
                        break
                if not sort_label:
                    sort_label = "?sort_object"
        return sort_label

    @property
    def sortby(self):
        SORT_CLAUSE = u"ORDER BY %(sort_order)s(%(variable)s)"
        sort_variable = self.get_sort_variable()
        statement = ""
        if sort_variable:
            statement = SORT_CLAUSE % {
                "sort_order": self.params["sort_order"].upper(),
                "variable": sort_variable
            }
        return statement

    @property
    def variables(self):
        items = ["?label", "?subject"]

        for predicate, object_, index in self.po_tuples:
            if self.should_add_predicate_and_object(predicate, object_):
                if predicate.startswith("?"):
                    items.append(predicate)
                elif object_.startswith("?"):
                    items.append(object_)

        sort_variable = self.get_sort_variable()
        if sort_variable:
            items.append(sort_variable)

        items = sorted(set(items))
        return ", ".join(items)

    def to_string(self, count=False):
        params = dict(inspect.getmembers(self), **self.params)
        if count:
            query_string = self.skeleton_count % params
        else:
            query_string = self.skeleton % params
        return query_string


def query_filter_instances(query_params):
    query = Query(query_params).to_string()
    query_response = triplestore.query_sparql(query, query_params.triplestore_config)
    return query_response


def query_count_filter_instances(query_params):
    query = Query(query_params).to_string(count=True)
    query_response = triplestore.query_sparql(query, query_params.triplestore_config)
    return query_response


def merge_by_id(items_list):
    """
    Provided two SPARQL Response rows that map the same @id,
    merge them, replacing property's value by a list containing
    all mapped values.
    """
    items_dict = {}
    index = 0
    pending_items = len(items_list)

    while pending_items:
        item = items_list[index]
        uid = item["@id"]
        existing_item = items_dict.get(uid)
        if not existing_item:
            items_dict[uid] = item
            index += 1
        else:
            for (key, old_value) in existing_item.items():
                new_value = item[key]
                if isinstance(old_value, list) and not (new_value in old_value):
                    old_value.append(new_value)
                elif new_value != old_value:
                    existing_item[key] = [old_value, new_value]
            items_list.pop(index)
        pending_items -= 1
    return items_list


# TODO: unit test, move to urls
def extract_prefix(url):
    prefix = url.rsplit('/', 1)[0]
    return u"{0}/".format(prefix)


# TODO: unit test
def add_prefix(items_list, class_prefix):
    for item in items_list:
        uri = item["@id"]
        item["instance_prefix"] = extract_prefix(uri)
        item["class_prefix"] = class_prefix


def filter_instances(query_params):
    if not class_exists(query_params):
        error_message = u"Class {0} in graph {1} does not exist".format(
            query_params["class_uri"], query_params["graph_uri"])
        raise HTTPError(404, log_message=error_message)

    keymap = {
        "label": "title",
        "subject": "@id",
        "sort_object": shorten_uri(query_params["sort_by"]),
    }
    for p, o, index in extract_po_tuples(query_params):
        keymap[o[1:]] = shorten_uri(p)

    result_dict = query_filter_instances(query_params)
    if not result_dict or not result_dict['results']['bindings']:
        return None
    items_list = compress_keys_and_values(result_dict, keymap=keymap, ignore_keys=["total"])
    items_list = merge_by_id(items_list)
    add_prefix(items_list, query_params['class_prefix'])
    decorate_with_resource_id(items_list)
    return build_json(items_list, query_params)


# TO-DO unittest
def cast_item(item, property_to_type):
    new_item = {}
    for property_, value in item.items():
        type_ = property_to_type.get(property_)
        if not type_ is None:
            if isinstance(value, list):
                value = [type_(v) for v in value]
                value = sorted(value)
            elif type_ is bool:
                value = bool(int(value))
            else:
                value = type_(value)
        new_item[property_] = value
    return new_item


# TO-DO unittest
def build_map_property_to_type(properties):
    """
    Based on a dictionary with class schema properties, return dict map from
    which maps property name to python object type.
    """
    return {prop: rdf_to_type[info["datatype"]] for prop, info in properties.items() if "datatype" in info}


# to-do: unittest
def cast_items_values(items_list, class_properties):
    """
    Provided a list o items (dicts), cast all values based on properties' types.
    """
    property_to_type = build_map_property_to_type(class_properties)
    new_list = []
    for item in items_list:
        new_item = cast_item(item, property_to_type)
        new_list.append(new_item)
    return new_list


def build_json(items_list, query_params):
    class_url = build_class_url(query_params)
    schema_url = unquote(build_schema_url_for_instance(query_params, class_url))

    class_properties = get_class.get_cached_schema(query_params)["properties"]
    items_list = cast_items_values(items_list, class_properties)
    
    json = {
        '_schema_url': schema_url,
        'pattern': '',
        '_class_prefix': query_params['class_prefix'],
        '_base_url': remove_last_slash(query_params.base_url),
        'items': items_list,
        '@context': {"@language": query_params.get("lang")},
        '@id': query_params['class_uri']
    }

    def calculate_total_items():
        result_dict = query_count_filter_instances(query_params)
        total_items = int(get_one_value(result_dict, 'total'))
        return total_items

    decorate_dict_with_pagination(json, query_params, calculate_total_items)

    return json


QUERY_CLASS_EXISTS = u"""
ASK {
  GRAPH <%(graph_uri)s> {<%(class_uri)s> a owl:Class}
}
"""


def class_exists(query_params):
    query = QUERY_CLASS_EXISTS % query_params
    query_result = triplestore.query_sparql(query, query_params.triplestore_config)
    return is_result_true(query_result)
