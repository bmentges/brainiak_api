# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, HTTPError, RequestHandler

from brainiak import settings, triplestore
from brainiak import __version__
from brainiak.schema.resource import get_schema
#from brainiak.resource.instance import get_instance


class HealthcheckResource(RequestHandler):

    def get(self):
        self.write("WORKING")


class VersionResource(RequestHandler):

    def get(self):
        self.write(__version__)


class VirtuosoStatusResource(RequestHandler):

    def get(self):
        if settings.ENVIRONMENT == 'prod':
            raise HTTPError(404)

        self.write(triplestore.status())


class SchemaResource(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaResource, self).__init__(*args, **kwargs)

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

    # @asynchronous
    # @gen.engine
    # def post(self, context_name, collection_name, schema_name):
    #     #data = yield gen.Task(self._entities.add, context_name, collection_name, self.request.body)
    #     self.set_status(201)
    #     #self.set_header('Location', headers.location(self.request, data['slug']))
    #     self.finish()


# class InstanceResource(RequestHandler):

#     def __init__(self, *args, **kwargs):
#         super(InstanceResource, self).__init__(*args, **kwargs)

#     @asynchronous
#     @gen.engine
#     def get(self, context_name, schema_name, instance_id):
#         response = yield gen.Task(get_instance, context_name, schema_name, instance_id)
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.write(response)
#         self.finish()
