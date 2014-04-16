import copy

from tornado.web import HTTPError

from brainiak import log
from brainiak.triplestore import query_sparql
from brainiak.utils.i18n import _
from brainiak.utils.sparql import compress_keys_and_values


QUERY_EXECUTION_LOG_FORMAT = "Stored Query [{query_id}] - app {app_name} - {url} - {query}"

NO_RESULTS_MESSAGE_FORMAT = "The query returned no results. SPARQL endpoint [{0}]\n  Query: {1}"


def execute_query(query_id, stored_query, querystring_params):
    query = get_query(stored_query, querystring_params)

    # TODO extract_method?
    request_dict = copy.copy(querystring_params.triplestore_config)
    request_dict.update({"query_id": query_id})
    request_dict.update({"query": query})
    log.logger.info(QUERY_EXECUTION_LOG_FORMAT.format(**request_dict))

    result_dict = query_sparql(query,
                               querystring_params.triplestore_config)
    items = compress_keys_and_values(result_dict)
    if not items:
        message = NO_RESULTS_MESSAGE_FORMAT.format(querystring_params.triplestore_config["url"], query)
        return {
            "items": [],
            # TODO explain in which instance of Virtuoso the query was executed?
            "warning": message}
    return {"items": items}


def get_query(stored_query, querystring_params):
    # template existence is validated in stored query creation/modification
    template = stored_query["sparql_template"]
    try:
        # .arguments is a dict with decoded querystring params
        query = template % querystring_params.arguments
        return query
    except KeyError as key_error:
        missing_key_message = _("Missing key '{0}' in querystring.\n  Template: {1}").format(key_error.args[0], template)
        raise HTTPError(400, log_message=missing_key_message)
