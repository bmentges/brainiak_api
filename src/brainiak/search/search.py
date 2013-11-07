# -*- coding: utf-8 -*-
from tornado.web import HTTPError


def do_search(query_params):

    if not 'pattern' in query_params:
        message = u"Required parameter 'pattern' was not given to search service"
        raise HTTPError(400, message)

    response = {}
    return response
