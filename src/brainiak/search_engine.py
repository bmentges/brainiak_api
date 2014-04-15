import json
import time
import urllib

from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPError as ClientHTTPError

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.settings import ELASTICSEARCH_ENDPOINT


REQUEST_LOG_FORMAT = u"ELASTICSEARCH - %(method)s - %(url)s - %(status)s - [time: %(time_diff)s] - REQUEST BODY - %(request_body)s - RESPONSE BODY - %(response_body)s"


class ElasticSearchException(Exception):
    pass


def run_search(body, indexes=None):
    request_url = _build_elasticsearch_request_url(indexes)

    request_params = {
        "url": unicode(request_url),
        "method": "POST",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
        "body": unicode(json.dumps(body))
    }

    response = _get_response(request_params)

    return json.loads(response.body)


def _build_elasticsearch_request_url(indexes):
    request_url = "http://" + ELASTICSEARCH_ENDPOINT + "/"

    if indexes is not None:
        request_url += ",".join(indexes) + "/"
    else:
        request_url += "semantica.*/"

    request_url += "_search"

    return request_url


def run_analyze(target, analyzer, indexes):
    request_url = _build_elasticsearch_analyze_url(indexes, analyzer, target)
    request_params = {
        "url": unicode(request_url),
        "method": "GET",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
    }

    response = _get_response(request_params)

    return json.loads(response.body)


def _build_elasticsearch_analyze_url(indexes, analyzer, target):
    index_path = ",".join(indexes) if isinstance(indexes, list) else indexes

    if isinstance(target, unicode):
        target = urllib.quote_plus(target.encode('utf-8'))
    else:
        target = urllib.quote_plus(target)

    if analyzer != "default":
        request_url = "http://{0}/{1}/_analyze?analyzer={2}&text={3}".format(
            ELASTICSEARCH_ENDPOINT, index_path, analyzer, target)
    else:
        request_url = "http://{0}/{1}/_analyze?text={2}".format(
            ELASTICSEARCH_ENDPOINT, index_path, target)
    return request_url


def save_instance(entry, index_name, type_name, instance_id):
    request_url = "http://{0}/{1}/{2}/{3}".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name, instance_id)

    request_params = {
        "url": unicode(request_url),
        "method": "PUT",
        "body": unicode(json.dumps(entry))
    }

    response = _get_response(request_params)

    return response.code


def get_instance(index_name, type_name, instance_id):
    request_url = "http://{0}/{1}/{2}/{3}".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name, instance_id)

    request_params = {
        "url": unicode(request_url),
        "method": "GET"
    }

    response = _get_response(request_params)

    if response is not None:
        return json.loads(response.body)

def get_all_instances_from_type(index_name, type_name, offset, per_page):
    request_url = "http://{0}/{1}/{2}/_search".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name)

    request_body = {
        "query" : {"match_all" : {}},
        "fields": ["sparql_template", "description"],
        "from": offset,
        "size": per_page
    }

    request_params = {
        "url": unicode(request_url),
        "method": "POST",
        "body": unicode(json.dumps(request_body))
    }

    response = _get_response(request_params)

    # TODO refactor response handling
    if response is not None:
        return json.loads(response.body)


def delete_instance(index_name, type_name, instance_id):
    request_url = "http://{0}/{1}/{2}/{3}".format(
        ELASTICSEARCH_ENDPOINT, index_name, type_name, instance_id)

    request_params = {
        "url": unicode(request_url),
        "method": "DELETE",
        "allow_nonstandard_methods": True
    }

    response = _get_response(request_params)

    return response is not None


def _do_request(request_params):
    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()
    time_diff = time_f - time_i

    request_params["status"] = response.code
    request_params["time_diff"] = time_diff
    request_params["response_body"] = response.body
    request_params["request_body"] = request_params.get("body", "")

    log_msg = REQUEST_LOG_FORMAT % request_params
    log.logger.info(log_msg)

    return response


def _get_response(request_params):
    try:
        response = _do_request(request_params)
        return response
    except ClientHTTPError as e:
        # Throwing explictly tornado.httpclient.ClientHTTPError so that
        #   handler can detect it as a backend service error
        if e.code == 404:
            return None
        else:
            raise e
