# -*- coding: utf-8 -*-

from tornado.testing import AsyncHTTPTestCase
from brainiak.server import Application
#from tests import TornadoAsyncHTTPTestCase


class SchemaResourceTestCase(AsyncHTTPTestCase):

    def get_app(self):
        return Application(debug=True)

    def test_schema_person_returns_200_and_json(self):
        response = self.fetch('/contexts/test/schemas/person')
        self.assertEquals(response.code, 200)
