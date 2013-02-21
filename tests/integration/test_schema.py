# -*- coding: utf-8 -*-

from tornado.testing import AsyncHTTPTestCase
from brainiak.server import Application
from tests import TornadoAsyncHTTPTestCase


# class SchemaResourceTestCase():
#
#     def get_app(self):
#         return Application(debug=True)
#
#     # def handle_reponse_200(self, response):
#     #     self.assertEquals(response.code, 200)
#     #     self.stop()
#
#     def test_schema_person_returns_200_and_json(self):
#         self.assert_(True)
#         # FIXME
#         #response = self.fetch('/contexts/person/schemas/Person', callback=self.handle_reponse_200)
