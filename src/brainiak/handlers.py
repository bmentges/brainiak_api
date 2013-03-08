# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, HTTPError, RequestHandler

from brainiak import settings, triplestore
from brainiak import __version__
from brainiak.schema.resource import get_schema
from brainiak.instance.resource import get_instance


class HealthcheckHandler(RequestHandler):

    def get(self):
        self.write("WORKING")


class VersionHandler(RequestHandler):

    def get(self):
        self.write(__version__)


class VirtuosoStatusHandler(RequestHandler):

    def get(self):
        if settings.ENVIRONMENT == 'prod':
            raise HTTPError(404)

        self.write(triplestore.status())


class SchemaHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaHandler, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def get(self, context_name, class_name):
        response = yield gen.Task(get_schema, context_name, class_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(204)
        else:
            self.write(response)
        self.finish()


class InstanceHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceHandler, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def get(self, context_name, class_name, instance_id):
        response = yield gen.Task(get_instance, context_name, class_name, instance_id)
        self.set_header('Access-Control-Allow-Origin', '*')
        if response is None:
            self.set_status(204)
        else:
            # TODO JSON parsing to JSON Schema format
            self.write(response)
        self.finish()

#localhost:5100/person/Person/_filter?predicate=person:Joao
#localhost:5100/person/Person/_filter?predicate=http://Joao
#localhost:5100/person/Person/_filter?object=http://Falou


class InstanceFilterHandler(RequestHandler):

    DEFAULT_PER_PAGE = "10"
    DEFAULT_PAGE = "0"

    def __init__(self, *args, **kwargs):
        super(InstanceFilterResource, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def get(self, context_name, class_name):
        query_params = {
            "class_uri": "{0}/{1}/{2}".format(settings.URI_PREFIX, context_name, class_name),
            "page": self.DEFAULT_PAGE,
            "per_page": self.DEFAULT_PER_PAGE,
            "predicate": "?predicate",
            "object": "?object"}

        for (query_param, default_value) in optional_params.items():
            optional_params[query_param] = self.get_argument(query_param, default_value)
        # FIXME: UNDER DEV!!!
