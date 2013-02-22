# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, RequestHandler

from brainiak import triplestore
from brainiak.__init__ import __version__
from brainiak.schema_resource import get_schema
from brainiak.instance_resource import get_instance



class HealthcheckResource(RequestHandler):

    def get(self):
        self.write("WORKING")


class VersionResource(RequestHandler):

    def get(self):
        self.write(__version__)


class VirtuosoStatusResource(RequestHandler):

    def get(self):
        self.write(triplestore.status())


class SchemaResource(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaResource, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def get(self, context_name, schema_name):
        response = yield gen.Task(get_schema, context_name, schema_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(response)
        self.finish()

    # @asynchronous
    # @gen.engine
    # def post(self, context_name, collection_name, schema_name):
    #     #data = yield gen.Task(self._entities.add, context_name, collection_name, self.request.body)
    #     self.set_status(201)
    #     #self.set_header('Location', headers.location(self.request, data['slug']))
    #     self.finish()


class InstanceResource(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(InstanceResource, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def get(self, context_name, schema_name):
        response = yield gen.Task(get_instance, context_name, schema_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write(response)
        self.finish()
