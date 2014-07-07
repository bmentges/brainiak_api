import json

import requests
import tornado
from tornado.httputil import HTTPHeaders
from tests.sparql import QueryTestCase
from tests.tornado_cases import _curl_setup_request, TornadoAsyncHTTPTestCase
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase
from brainiak import server


# Util tornado 3.1.0.0, tornado.curl_httpclient ignores payloads (body) of
# custom methods.
#
# We fixed this and proposed a pull request to tornado:
# https://github.com/tornadoweb/tornado/pull/1090
#
# While this issue is not fixed (1/7/2014), we are monkey patching
# tornado.curl_httpclient's _curl_setup_request.

#print("Temporary mockey-patch to tornado/curl_httpclient.py")
#tornado.curl_httpclient._curl_setup_request = _curl_setup_request


class PatchInstanceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures_by_graph = {"http://on.to/": ["tests/sample/people.ttl"]}

    def get_app(self):
        return server.Application()

    def test_patch_suceeds(self):
        data = {
            "instance": "http://on.to/flipperTheDolphin",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&meta_properties={meta}&lang=en'
        url = url.format(**data)

        # Check original state
        response = self.fetch(url, method='GET')
        computed = json.loads(response.body)
        self.assertEqual(response.code, 200)
        expected = {
            u'http://on.to/weight': 200.0,
            u'http://on.to/isHuman': False,
            u'http://on.to/name': u'Flipper',
            u'http://on.to/age': 4,
            u'rdf:type': u'http://on.to/Person'
        }
        self.assertEqual(computed, expected)

        patch_list = [
            {
                "op": "replace",
                "path": "http://on.to/age",
                "value": 5
            }
        ]

        response = self.fetch(url, method='PATCH', body=json.dumps(patch_list))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, "")

        # Check if it was updated
        response = self.fetch(url, method='GET')
        computed = json.loads(response.body)
        expected = {
            u'http://on.to/weight': 200.0,
            u'http://on.to/isHuman': False,
            u'http://on.to/name': u'Flipper',
            u'http://on.to/age': 5,
            u'rdf:type': u'http://on.to/Person'
        }
        self.assertEqual(computed, expected)

    def test_patch_fails_due_to_inexistent_instance(self):
        data = {
            "instance": "http://on.to/Beethoven",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&meta_properties={meta}&lang=en'
        url = url.format(**data)

        response = self.fetch(url, method='PATCH', body=json.dumps(data))
        self.assertEqual(response.code, 404)
        computed_msg = json.loads(response.body)
        expected_msg = {"errors": ["HTTP error: 404\nInexistent instance"]}
        self.assertEqual(computed_msg, expected_msg)

    def test_patch_fails_due_to_removal_of_obligatory_field(self):
        data = {
            "instance": "http://on.to/flipperTheDolphin",
            "class": "http://on.to/Person",
            "graph": "http://on.to/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&meta_properties={meta}&lang=en'
        url = url.format(**data)

        patch_list = [
            {
                u'path': 'http://on.to/name',
                u'op': u'remove'
            }
        ]

        response = self.fetch(url, method='PATCH', body=json.dumps(patch_list))
        self.assertEqual(response.code, 400)
        computed_msg = json.loads(response.body)
        expected_msg = {"errors": ["HTTP error: 400\nLabel properties like rdfs:label or its subproperties are required"]}
        self.assertEqual(computed_msg, expected_msg)
