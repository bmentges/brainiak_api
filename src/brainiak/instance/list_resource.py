import inspect

from brainiak import settings, triplestore
from brainiak.prefixes import shorten_uri
from brainiak.utils.links import build_class_url, build_schema_url, collection_links, add_link, filter_query_string_by_key_prefix, remove_last_slash, self_link
from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import compress_keys_and_values, normalize_term, calculate_offset


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

    skeleton = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT %(variables)s
        WHERE {
            %(triples)s
            %(filter)s
        }
        %(sortby)s
        LIMIT %(per_page)s
        OFFSET %(offset)s
    """

    skeleton_count = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
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
        rdfs_repetition = (predicate == "rdfs:label") and object_.startswith("?")

        return not generic_po and not rdfs_repetition

    @property
    def triples(self):
        tuples = [
            ("a", "<%(class_uri)s>"),
            ("rdfs:label", "?label")
        ]

        predicate = self.params["p"]
        object_ = self.params["o"]
        if self.should_add_predicate_and_object(predicate, object_):
            predicate = normalize_term(predicate, self.params["lang"])
            object_ = normalize_term(object_, self.params["lang"])
            tuples.append((predicate, object_))

        sort_object = self.get_sort_variable()
        sort_sufix = ""
        if sort_object == "?sort_object":
            sort_predicate = normalize_term(self.params["sort_by"])
            if self.params["sort_include_empty"] == "1":
                sort_sufix = "OPTIONAL {?subject %s ?sort_object}" % sort_predicate
            else:
                tuples.append((sort_predicate, sort_object))

        tuples_strings = ["%s %s" % each_tuple for each_tuple in tuples]
        statement = "?subject " + " ;\n".join(tuples_strings) + " .\n" + sort_sufix
        statements = statement % self.params

        return 'GRAPH ?g { %s }' % statements

    @property
    def filter(self):
        translatables = ["?label"]
        statement = ""
        filter_list = []
        FILTER_CLAUSE = 'FILTER(langMatches(lang(%(variable)s), "%(lang)s") OR langMatches(lang(%(variable)s), "")) .'
        if self.params["lang"]:
            for variable in translatables:
                statement = FILTER_CLAUSE % {
                    "variable": variable,
                    "lang": self.params["lang"]
                }
                filter_list.append(statement)

        filter_list.append("FILTER(?g = <%(graph_uri)s>) ." % self.params)
        if filter_list:
            statement = "\n".join(filter_list)

        return statement

    @property
    def offset(self):
        return calculate_offset(self.params, settings.DEFAULT_PAGE, settings.DEFAULT_PER_PAGE)

    def get_sort_variable(self):
        sort_predicate = self.params["sort_by"]
        if sort_predicate:
            sort_predicate = shorten_uri(sort_predicate) if not sort_predicate.startswith("?") else sort_predicate

            predicate = self.params["p"]
            predicate = shorten_uri(predicate) if not predicate.startswith("?") else predicate

            object_ = self.params["o"]

            sort_label = "?sort_object"
            if (sort_predicate == "rdfs:label"):
                sort_label = "?label"
            elif (sort_predicate == predicate) and object_.startswith("?"):
                sort_label = object_
            elif (sort_predicate == predicate) and not object_.startswith("?"):
                sort_label = ""
        else:
            sort_label = ""

        return sort_label

    @property
    def sortby(self):
        SORT_CLAUSE = "ORDER BY %(sort_order)s(%(variable)s)"
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

        predicate = self.params["p"]
        object_ = self.params["o"]
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
    query_response = triplestore.query_sparql(query)
    return query_response


def query_count_filter_instances(query_params):
    query = Query(query_params).to_string(count=True)
    query_response = triplestore.query_sparql(query)
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
    return "{0}/".format(prefix)


# TODO: unit test
def add_instance_prefix(items_list):
    for item in items_list:
        uri = item["@id"]
        item["instance_prefix"] = extract_prefix(uri)


def filter_instances(query_params):
    keymap = {
        "label": "title",
        "subject": "@id",
        "sort_object": shorten_uri(query_params["sort_by"]),
        "object": shorten_uri(query_params["p"]),
    }
    result_dict = query_filter_instances(query_params)
    if not result_dict or not result_dict['results']['bindings']:
        return None
    items_list = compress_keys_and_values(result_dict, keymap=keymap, ignore_keys=["total"])
    items_list = merge_by_id(items_list)
    add_instance_prefix(items_list)
    decorate_with_resource_id(items_list)
    return build_json(items_list, query_params)


def build_json(items_list, query_params):
    base_url = remove_last_slash(query_params.base_url)
    links = self_link(query_params) + collection_links(query_params)
    query_string = filter_query_string_by_key_prefix(query_params["request"].query, ["class", "graph"])
    create_url = build_class_url(query_params, include_query_string=True)
    schema_url = build_schema_url(query_params)

    if query_string:
        item_query_string = query_string + "&" + "instance_prefix={instance_prefix}"
    else:
        item_query_string = query_string + "instance_prefix={instance_prefix}"
    item_url = "{0}/{{resource_id}}?{1}".format(base_url, item_query_string)

    add_link(links, 'item', item_url)
    add_link(links, "create", create_url, method='POST', schema={'$ref': schema_url})
    json = {
        'items': items_list,
        'links': links,
        "@context": {"@language": query_params.get("lang")}
    }
    return json
