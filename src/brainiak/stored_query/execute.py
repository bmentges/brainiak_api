from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.utils.i18n import _
from brainiak.utils.sparql import compress_keys_and_values


def execute_query(stored_query, querystring_params):
    query = get_query(stored_query, querystring_params)
    result_dict = triplestore.query_sparql(query,
                                           querystring_params.triplestore_config)
    items_dict = compress_keys_and_values(result_dict)
    return {"items": items_dict}


def get_query(stored_query, querystring_params):
    # template existence is validated in stored query creation/modification
    template = stored_query["sparql_template"]
    try:
        query = template % querystring_params.arguments
        return query
    except KeyError as key_error:
        missing_key_message = _("Missing key {0} in querystring").format(key_error.args[0])
        raise HTTPError(400, log_message=missing_key_message)
