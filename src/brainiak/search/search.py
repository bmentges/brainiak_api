# -*- coding: utf-8 -*-
from tornado.web import HTTPError

from brainiak import settings
from brainiak.prefixes import uri_to_slug
from brainiak.search_engine import run_search
from brainiak.utils import resources


def do_search(query_params):

    if not 'pattern' in query_params:
        message = u"Required parameter 'pattern' was not given to search service"
        raise HTTPError(400, message)

    search_fields = None
    elasticsearch_result = do_search_query(query_params, search_fields)

    response = parse_result(elasticsearch_result)
    return response


def do_search_query(query_params, search_fields):
    ELASTICSEARCH_QUERY_DICT = {
        "filter": {
            "type": {
                "value": query_params["class_uri"]
            }
        },
        "query": {
            "query_string": {
                "fields": search_fields,
                "query": "*{0}*".format(query_params["pattern"])
            }
        },
        "from": int(resources.calculate_offset(query_params)),
        "size": int(query_params.get("per_page", settings.DEFAULT_PER_PAGE)),
    }

    indexes = ["semantica." + uri_to_slug(query_params["graph_uri"])]
    elasticsearch_result = run_search(ELASTICSEARCH_QUERY_DICT, indexes=indexes)
    return elasticsearch_result


def parse_result(elasticsearch_result):
    return elasticsearch_result
