import json
import time
import urllib

from tornado.httpclient import HTTPRequest

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.settings import ELASTICSEARCH_ENDPOINT


format_post = u"ELASTICSEARCH - %(url)s - %(method)s [time: %(time_diff)s] - QUERY - %(body)s"


def run_search(body, indexes=None):
    request_url = _build_elasticsearch_request_url(indexes)

    request_params = {
        "url": unicode(request_url),
        "method": u"POST",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
        "body": unicode(json.dumps(body))
    }
    #import pdb; pdb.set_trace()
    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()

    request_params["time_diff"] = time_f - time_i
    log_msg = format_post % request_params
    log.logger.info(log_msg)

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
        "method": u"GET",
        "headers": {u"Content-Type": u"application/x-www-form-urlencoded"},
    }

    request = HTTPRequest(**request_params)
    response = greenlet_fetch(request)
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
