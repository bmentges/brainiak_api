import json

from mock import patch

from brainiak.context import get_context
from brainiak import greenlet_tornado
from brainiak.utils.sparql import compress_keys_and_values

from tests.mocks import Params
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class ListClassesResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    fixtures = ["tests/sample/schemas.n3"]
    graph_uri = "http://example.onto/"

    maxDiff = None

    @patch("brainiak.handlers.logger")
    def test_list_classes_two_pages_in_sequence(self, log):
        response_page1 = self.fetch('/test/?page=1&per_page=2&graph_uri={0}'.format(self.graph_uri), method='GET')
        self.assertEqual(response_page1.code, 200)
        response_page2 = self.fetch('/test/?page=2&per_page=2&graph_uri={0}'.format(self.graph_uri), method='GET')
        self.assertEqual(response_page2.code, 200)
        response1 = json.loads(response_page1.body)
        response2 = json.loads(response_page2.body)
        set1 = {i[u"@id"] for i in response1['items']}
        set2 = {i[u"@id"] for i in response2['items']}
        self.assertFalse(set1.intersection(set2))

    @patch("brainiak.handlers.logger")
    def test_list_classes_400(self, log):
        response = self.fetch('/test/?wrong_param=1', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.logger")
    def test_list_classes_500(self, log):
        config = {"side_effect": NotImplementedError}
        patcher = patch("brainiak.handlers.list_classes", ** config)
        patcher.start()

        response = self.fetch('/test/', method='GET')
        self.assertEqual(response.code, 500)
        patcher.stop()

    @patch("brainiak.handlers.logger")
    @patch("brainiak.context.get_context.graph_exists", return_value=True)
    def test_list_classes_empty(self, mocked_graph_exists, log):
        original_graph_uri = self.graph_uri
        self.graph_uri = "http://empty.graph"
        response = self.fetch('/test/?graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body)["items"], [])
        self.graph_uri = original_graph_uri

    @patch("brainiak.handlers.logger")
    def test_graph_does_not_exists(self, log):
        original_graph_uri = self.graph_uri
        self.graph_uri = "http://empty.graph"
        response = self.fetch('/test/?graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 404)
        self.graph_uri = original_graph_uri

    @patch("brainiak.handlers.logger")
    def test_list_classes_200(self, log):
        expected_items = [
            {"@id": "http://example.onto/Place", "title": "Lugar", "resource_id": "Place", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/PlaceWithoutLanguage", "title": "Place", "resource_id": "PlaceWithoutLanguage", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/Lugar", "title": "Lugar", "resource_id": "Lugar", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/City", "title": "Cidade", "resource_id": "City", "class_prefix": "http://example.onto/"}
        ]

        response = self.fetch('/test/?graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 200)
        response_json_dict = json.loads(response.body)
        self.assertItemsEqual(expected_items, response_json_dict["items"])

    @patch("brainiak.handlers.logger")
    def test_list_classes_200_with_count(self, log):
        expected_items = [
            {"@id": "http://example.onto/Place", "title": "Lugar", "resource_id": "Place", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/PlaceWithoutLanguage", "title": "Place", "resource_id": "PlaceWithoutLanguage", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/Lugar", "title": "Lugar", "resource_id": "Lugar", "class_prefix": "http://example.onto/"},
            {"@id": "http://example.onto/City", "title": "Cidade", "resource_id": "City", "class_prefix": "http://example.onto/"}
        ]

        response = self.fetch('/test/?do_item_count=1&graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 200)
        response_json_dict = json.loads(response.body)

        keys = response_json_dict.keys()
        self.assertEqual(len(keys), 7)

        self.assertIn("items", keys)
        self.assertIn('item_count', keys)
        self.assertIn('_base_url', keys)
        self.assertIn('_first_args', keys)
        self.assertIn('_last_args', keys)
        self.assertIn('@context', keys)
        self.assertIn('@id', keys)

        self.assertItemsEqual(expected_items, response_json_dict["items"])

    @greenlet_tornado.greenlet_test
    def test_query(self):
        expected_classes = [
            {u'class': u'http://example.onto/PlaceWithoutLanguage', u'label': u'Place'},
            {u'class': u'http://example.onto/Lugar', u'label': u'Lugar'},
            {u'class': u'http://example.onto/Place', u'label': u'Lugar'},
            {u'class': u'http://example.onto/City', u'label': u'Cidade'}]
        query_params = Params({
            "graph_uri": self.graph_uri,
            "lang": "pt",
            "page": 0,
            "per_page": 10,
            'lang_filter_label': '\n    FILTER(langMatches(lang(?label), "pt") OR langMatches(lang(?label), "")) .\n'
        })
        response = get_context.query_classes_list(query_params)
        compressed_response = compress_keys_and_values(response)
        self.assertItemsEqual(expected_classes, compressed_response)
