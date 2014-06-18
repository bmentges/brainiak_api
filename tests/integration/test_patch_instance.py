import json
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class PatchInstanceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures = ["tests/sample/people.ttl"]
    graph_uri = "http://test.com/"

    def test_patch_suceeds(self):
        data = {
            "instance": "http://on.to/flipperTheDolphin",
            "class": "http://on.to/Person",
            "graph": "http://test.com/",
            "meta": "0"
        }
        url = '/_/_/_/?graph_uri={graph}&class_uri={class}&instance_uri={instance}&meta_properties={meta}&lang=en'
        url = url.format(**data)

        # Check original state
        response = self.fetch(url, method='GET')
        computed = json.loads(response.body)
        expected = {
            u'http://on.to/weight': 200.0,
            u'http://on.to/isHuman': False,
            u'http://on.to/name': u'Flipper',
            u'http://on.to/age': 4,
            u'rdf:type': u'http://on.to/Person'
        }
        self.assertEqual(computed, expected)

        # Change birthcity
        data = {u'http://on.to/age': 5}
        response = self.fetch(url, method='PATCH', body=json.dumps(data))
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
