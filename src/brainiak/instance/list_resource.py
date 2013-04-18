import inspect

from brainiak import settings, triplestore
from brainiak.prefixes import expand_uri, PrefixError, shorten_uri
from brainiak.utils.links import build_links
from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import compress_keys_and_values, get_one_value, \
    add_language_support


# TODO: move to sparql utils
# TODO: unit test
def normalize_term(term, language=""):
    language_tag = "@%s" % language if language else ""
    if (not term.startswith("?")):
        if (":" in term):
            try:
                term = "<%s>" % expand_uri(term)
            except PrefixError:
                pass
        else:
            term = '"%s"%s' % (term, language_tag)
    return term


class Query(object):

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
        if sort_object == "?sort_object":
            sort_predicate = normalize_term(self.params["sort_by"])
            tuples.append((sort_predicate, sort_object))

        tuples_strings = ["%s %s" % each_tuple for each_tuple in tuples]
        statement = "?subject " + " ;\n".join(tuples_strings) + " ."

        return statement % self.params

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

        if filter_list:
            statement = "\n".join(filter_list)

        return statement

    @property
    def offset(self):
        page = int(self.params.get("page", settings.DEFAULT_PAGE))
        per_page = int(self.params.get("per_page", settings.DEFAULT_PER_PAGE))
        return str(page * per_page)

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


# TODO: unit test
def merge_by_id(items_list):
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


def filter_instances(query_params):
    result_dict = query_count_filter_instances(query_params)

    total_items = int(get_one_value(result_dict, 'total'))

    if not total_items:
        return None

    keymap = {
        "label": "title",
        "subject": "@id",
        "sort_object": shorten_uri(query_params["sort_by"]),
        "object": shorten_uri(query_params["p"]),
    }
    result_dict = query_filter_instances(query_params)
    items_list = compress_keys_and_values(result_dict, keymap=keymap, ignore_keys=["total"])
    items_list = merge_by_id(items_list)
    decorate_with_resource_id(items_list)
    return build_json(items_list, total_items, query_params)


def build_json(items_list, total_items, query_params):
    request = query_params["request"]
    base_url = "{0}://{1}{2}".format(request.protocol, request.host, request.path)

    links = build_links(
        base_url,
        page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
        per_page=int(query_params["per_page"]),
        total_items=total_items,
        query_string=request.query)

    json = {
        'items': items_list,
        'item_count': total_items,
        'links': links,
        "@language": query_params.get("lang")
    }
    return json
