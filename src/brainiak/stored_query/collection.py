from brainiak.stored_query import ES_INDEX_NAME, ES_TYPE_NAME
from brainiak.search_engine import get_all_instances_from_type
from brainiak.settings import DEFAULT_PER_PAGE
from brainiak.utils.resources import decorate_dict_with_pagination, \
    calculate_offset


NO_RESULTS_MESSAGE_FORMAT = "There is no query stored"

def get_stored_queries(params):
    offset = int(calculate_offset(params))
    per_page = int(params.get("per_page", DEFAULT_PER_PAGE))

    stored_queries_result = get_all_instances_from_type(ES_INDEX_NAME,
                                                        ES_TYPE_NAME,
                                                        offset,
                                                        per_page)
    response_dict = _get_response_dict(stored_queries_result, params)
    return response_dict


def _get_response_dict(stored_queries_result, params):
    response_dict = {}
    total_items, items_dict = _get_items_dict(stored_queries_result)
    response_dict.update(items_dict)
    if not items_dict["items"]:
        response_dict.update({"warning": NO_RESULTS_MESSAGE_FORMAT})
    else:
        decorate_dict_with_pagination(response_dict, params, lambda: total_items)
    return response_dict


def _get_items_dict(stored_queries_result):
    items = []
    for query in stored_queries_result["hits"]["hits"]:
        item = {
            "resource_id": query["_id"]
        }
        item.update(query["fields"])
        items.append(item)
    items_dict = {"items": items}
    total_items = stored_queries_result["hits"]["total"]
    return total_items, items_dict
