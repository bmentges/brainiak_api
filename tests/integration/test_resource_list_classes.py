import json

from mock import patch

from brainiak.context import list_resource
from brainiak import greenlet_tornado
from brainiak.utils.sparql import compress_keys_and_values

from tests import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class ListClassesResourceTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/schemas.n3"]
    graph_uri = "http://example.onto/"

    maxDiff = None

    @patch("brainiak.handlers.log")
    def test_list_classes_400(self, log):
        response = self.fetch('/test/?wrong_param=1', method='GET')
        self.assertEqual(response.code, 400)

    @patch("brainiak.handlers.log")
    def test_list_classes_500(self, log):
        config = {"side_effect": NotImplementedError}
        patcher = patch("brainiak.handlers.list_classes", ** config)
        patcher.start()

        response = self.fetch('/test/', method='GET')
        self.assertEqual(response.code, 500)
        patcher.stop()

    @patch("brainiak.handlers.log")
    def test_list_classes_404(self, log):
        original_graph_uri = self.graph_uri
        self.graph_uri = "http://empty.graph"
        response = self.fetch('/test/?graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 404)
        self.graph_uri = original_graph_uri

    @patch("brainiak.handlers.log")
    def test_list_classes_200(self, log):
        expected_items = [
            {"@id": "http://example.onto/Place", "title": "Lugar", "resource_id": "Place"},
            {"@id": "http://example.onto/PlaceWithoutLanguage", "title": "Place", "resource_id": "PlaceWithoutLanguage"},
            {"@id": "http://example.onto/Lugar", "title": "Lugar", "resource_id": "Lugar"},
            {"@id": "http://example.onto/City", "title": "Cidade", "resource_id": "City"}
        ]

        response = self.fetch('/test/?graph_uri=' + self.graph_uri)
        self.assertEqual(response.code, 200)
        response_json_dict = json.loads(response.body)
        self.assertItemsEqual(expected_items, response_json_dict["items"])

    @greenlet_tornado.greenlet_test
    def test_query(self):
        expected_classes = [
            {u'class': u'http://example.onto/PlaceWithoutLanguage', u'label': u'Place'},
            {u'class': u'http://example.onto/Lugar', u'label': u'Lugar'},
            {u'class': u'http://example.onto/Place', u'label': u'Lugar'},
            {u'class': u'http://example.onto/City', u'label': u'Cidade'}]
        query_params = {
            "graph_uri": self.graph_uri,
            "lang": "pt",
            "page": 0,
            "per_page": 10,
            'lang_filter_label': '\n    FILTER(langMatches(lang(?label), "pt") OR langMatches(lang(?label), "")) .\n'
        }
        response = list_resource.query_classes_list(query_params)
        compressed_response = compress_keys_and_values(response)
        self.assertItemsEqual(expected_classes, compressed_response)
