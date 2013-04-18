import inspect

from brainiak import settings, triplestore
from brainiak.prefixes import expand_uri, shorten_uri
from brainiak.utils.links import build_links
from brainiak.utils.resources import decorate_with_resource_id
from brainiak.utils.sparql import compress_keys_and_values, get_one_value, \
    add_language_support


QUERY_COUNT_FILTER_INSTANCE = """
DEFINE input:inference <http://semantica.globo.com/ruleset>
SELECT DISTINCT count (distinct ?subject) as ?total
WHERE {
    ?subject a <%(class_uri)s> ;
             rdfs:label ?label %(po)s
    %(lang_filter_label)s
}
"""

QUERY_FILTER_INSTANCE = """
DEFINE input:inference <http://semantica.globo.com/ruleset>
SELECT DISTINCT ?subject, ?label
WHERE {
    ?subject a <%(class_uri)s> ;
             rdfs:label ?label %(po)s
    %(lang_filter_label)s
}
%(sort_by_statement)s
LIMIT %(per_page)s
OFFSET %(offset)s
"""

ORDER_BY = "ORDER BY %(sort_order)s(?sort_object)"


# TODO: move to sparql utils
# TODO: test
def normalize_term(term, language=""):
    language_tag = "@%s" % language if language else ""
    if (not term.startswith("?")):
        if (":" in term):
            term = "<%s>" % expand_uri(term)
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
        SELECT count(DISTINCT ?subject) as total
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


def process_params(query_params):
    """
    Important note: when "lang" is defined in query_params,
    the languge provided:
        - is applied to ALL literals of the query
        - labels will be filtered according to <lang>
    """
    potential_uris = ["o", "p", "sort_by"]
    (query_params, language_tag) = add_language_support(query_params, "label")

    for key in potential_uris:
        value = query_params.get(key, "")
        if value and (not value.startswith("?")):
            if (":" in value):
                query_params[key] = "<%s>" % expand_uri(value)
            else:
                query_params[key] = '"%s"%s' % (value, language_tag)

    if (query_params["p"] == "?predicate") and (query_params["o"] == "?object"):
        query_params["po"] = "."
    else:
        query_params["po"] = "; %(p)s %(o)s ." % query_params

    # TODO: the code bellow urges refactoring
    sort_property = query_params["sort_by"]
    if sort_property and (sort_property != "rdfs:label") and (sort_property != query_params["p"]):
        query_params["po"] = "; %(sort_by)s ?sort_object %(po)s" % query_params
        sort_by_statement = ORDER_BY % query_params
    elif sort_property == "rdfs:label":
        sort_by_statement = "ORDER BY %(sort_order)s(?label)" % query_params
    elif sort_property == query_params["p"] and query_params["o"] == "?object":
        sort_by_statement = "ORDER BY %(sort_order)s(?object)" % query_params
    elif (query_params["p"] != "?predicate") and (query_params["o"] != "?object"):
        sort_by_statement = ""
    else:
        sort_by_statement = ""
    query_params["sort_by_statement"] = sort_by_statement

    page = int(query_params.get("page", settings.DEFAULT_PAGE))
    per_page = int(query_params.get("per_page", settings.DEFAULT_PER_PAGE))
    query_params["offset"] = str(page * per_page)

    return query_params


def query_filter_instances(query_params):
    query = QUERY_FILTER_INSTANCE % query_params
    query_response = triplestore.query_sparql(query)
    return query_response


def query_count_filter_instances(query_params):
    query = QUERY_COUNT_FILTER_INSTANCE % query_params
    query_response = triplestore.query_sparql(query)
    return query_response


def filter_instances(query_params):
    predicate = query_params.get("p")
    sort_by = query_params.get("sort_by")
    query_params = process_params(query_params)
    result_dict = query_count_filter_instances(query_params)

    total_items = int(get_one_value(result_dict, 'total'))

    if not total_items:
        return None

    keymap = {"label": "title", "subject": "@id"}
    # if (query_params.get("o") == "?object") and (query_params["p"] != "<http://www.w3.org/2000/01/rdf-schema#label>") and (query_params["p"] != "?predicate"):
    #     keymap["object"] = shorten_uri(predicate)
    # if sort_by and (query_params.get("sort_by") != query_params.get("p")) and (query_params["sort_by"] != "<http://www.w3.org/2000/01/rdf-schema#label>"):
    #     keymap["sort_object"] = shorten_uri(sort_by)
    # if (query_params["sort_by"] == "<http://www.w3.org/2000/01/rdf-schema#label>"):
    #     keymap["sort_object"] = "title"
    result_dict = query_filter_instances(query_params)
    items_list = compress_keys_and_values(result_dict, keymap=keymap, ignore_keys=["total"])
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
