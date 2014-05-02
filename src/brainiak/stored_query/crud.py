import re

from brainiak.search_engine import save_instance, get_instance,\
    delete_instance
from brainiak.stored_query import ES_INDEX_NAME, ES_TYPE_NAME

from brainiak.utils.params import CLIENT_ID_HEADER

from tornado.web import HTTPError


FORBIDDEN_SPARUL_PATTERN = \
    re.compile(r"(^|\s+)(INSERT|MODIFY|DELETE|DROP|CLEAR|LOAD|CREATE|CONSTRUCT)\s",
               re.IGNORECASE | re.MULTILINE | re.UNICODE)
FORBIDDEN_SPARUL_MESSAGE = u"SPARUL queries (updates on triplestore) are not allowed"

MISSING_CLIENT_ID_MESSAGE = u"Missing X-Brainiak-Client-Id in headers"


def store_query(entry, query_id):
    if not _allowed_query(entry["sparql_template"]):
       raise HTTPError(400, log_message=FORBIDDEN_SPARUL_MESSAGE)

    if stored_query_exists(query_id):
        save_instance(entry, ES_INDEX_NAME, ES_TYPE_NAME, query_id)
        return 200
    else:
        save_instance(entry, ES_INDEX_NAME, ES_TYPE_NAME, query_id)
        return 201



def get_stored_query(query_id):
    stored_query = get_instance(ES_INDEX_NAME, ES_TYPE_NAME, query_id)
    if stored_query is not None:
        stored_query = stored_query["_source"]
        return stored_query


def stored_query_exists(query_id):
    return get_stored_query(query_id) is not None


def delete_stored_query(query_id):
    return delete_instance(ES_INDEX_NAME, ES_TYPE_NAME, query_id)


def validate_headers(headers):
    if not CLIENT_ID_HEADER in headers:
        raise HTTPError(400, log_message=MISSING_CLIENT_ID_MESSAGE)


def _allowed_query(query_template):
    query_template = re.sub(r'(/\*.+?\*/)', '', query_template, flags=re.DOTALL)
    match = FORBIDDEN_SPARUL_PATTERN.match(query_template)
    return match is None
