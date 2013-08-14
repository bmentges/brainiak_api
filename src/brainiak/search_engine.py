import time
import urllib

from tornado.httpclient import HTTPRequest

from brainiak import log
from brainiak.greenlet_tornado import greenlet_fetch
from brainiak.settings import ELASTICSEARCH_ENDPOINT


format_post = "ELASTICSEARCH - %(url)s - %(method)s [tempo: %(time_diff)s] - QUERY - %(body)s"


def run_search(body, indexes=None):
    request_url = _build_elasticsearch_request_url(indexes)

    request_params = {
        "url": request_url,
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "body": urllib.urlencode(body)
    }

    request = HTTPRequest(**request_params)
    time_i = time.time()
    response = greenlet_fetch(request)
    time_f = time.time()

    request_params["time_diff"] = time_f - time_i
    log_msg = format_post % request_params
    log.logger.info(log_msg)

    return response


def _build_elasticsearch_request_url(indexes):
    request_url = ELASTICSEARCH_ENDPOINT + "/"

    if indexes is not None:
        request_url += ",".join(indexes) + "/"
    else:
        request_url += "semantica.*/"

    request_url += "_search"

    return request_url
