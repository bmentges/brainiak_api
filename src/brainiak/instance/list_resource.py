from brainiak import triplestore
from brainiak.prefixes import expand_uri
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
SELECT DISTINCT ?subject ?label
WHERE {
    ?subject a <%(class_uri)s> ;
             rdfs:label ?label %(po)s
    %(lang_filter_label)s
}
LIMIT %(per_page)s
OFFSET %(page)s
"""


def process_params(query_params):
    """
    Important note: when "lang" is defined in query_params,
    the languge provided:
        - is applied to ALL literals of the query
        - labels will be filtered according to <lang>
    """
    potential_uris = ["o", "p"]
    (query_params, language_tag) = add_language_support(query_params, "label")

    for key in potential_uris:
        value = query_params.get(key, "")
        if (not value.startswith("?")):
            if (":" in value):
                query_params[key] = "<%s>" % expand_uri(value)
            else:
                query_params[key] = '"%s"%s' % (value, language_tag)

    if (query_params["p"] == "?predicate") and (query_params["o"] == "?object"):
        query_params["po"] = "."
    else:
        query_params["po"] = "; %(p)s %(o)s ." % query_params

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

    query_params = process_params(query_params)
    result_dict = query_count_filter_instances(query_params)

    total_items = int(get_one_value(result_dict, 'total'))

    if not total_items:
        return None

    result_dict = query_filter_instances(query_params)
    items_list = compress_keys_and_values(result_dict, keymap={"label": "title", "subject": "@id"}, ignore_keys=["total"])
    decorate_with_resource_id(items_list)
    return build_json(items_list, total_items, query_params)


def build_json(items_list, total_items, query_params):
    request = query_params["request"]
    class_url = 'http://{0}/{1}/{2}'.format(request.headers.get("Host"),
                                            query_params["context_name"],
                                            query_params["class_name"])

    links = build_links(
        request.path,
        #class_url,
        page=int(query_params["page"]) + 1,  # API's pagination begin with 1, Virtuoso's with 0
        per_page=int(query_params["per_page"]),
        request_url=request.uri,
        total_items=total_items,
        query_string=request.query)

    json = {
        'items': items_list,
        'item_count': total_items,
        'links': links,
        "@language": query_params.get("lang")
    }
    return json
