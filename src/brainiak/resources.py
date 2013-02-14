# -*- coding: utf-8 -*-

from tornado import gen
from tornado.web import asynchronous, RequestHandler


class SchemaResource(RequestHandler):

    def __init__(self, *args, **kwargs):
        super(SchemaResource, self).__init__(*args, **kwargs)

    @asynchronous
    @gen.engine
    def post(self, context_name, collection_name):
        #data = yield gen.Task(self._entities.add, context_name, collection_name, self.request.body)
        self.set_status(201)
        #self.set_header('Location', headers.location(self.request, data['slug']))
        self.finish()

    @asynchronous
    @gen.engine
    def get(self, context_name, collection_name):
        #data = yield gen.Task(self._entities.paginate, context_name, collection_name)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write('')
        self.finish()
