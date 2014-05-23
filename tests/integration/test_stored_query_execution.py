from mock import patch
from urllib import quote_plus

import requests
import ujson as json

from brainiak import settings
from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase

CLIENT_ID_HEADERS = {"X-Brainiak-Client-Id": "my_client_id"}


class StoredQueryCRUDExecution(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    fixtures = ["tests/sample/gender.n3"]
    graph_uri = "http://example.onto/"

    def setUp(self):
        super(StoredQueryCRUDExecution, self).setUp()
        self.delete_index()
        self.elastic_request_url = "http://{0}/brainiak/query/q".format(settings.ELASTICSEARCH_ENDPOINT)
        entry = {
            "sparql_template": "SELECT ?s FROM <%(g)s> {?s a owl:Class}",
            "description": ""
        }

        requests.put(self.elastic_request_url + "?refresh=true", data=json.dumps(entry))

    def delete_index(self):
        index_url = "http://{0}/brainiak".format(settings.ELASTICSEARCH_ENDPOINT)
        requests.delete(index_url)

    def tearDown(self):
        self.delete_index()
        super(StoredQueryCRUDExecution, self).tearDown()

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_get_query_result(self, mocked_lang):
        expected_response = {
            u"items": [{u"s": u"http://test.com/person/Gender"}]
        }

        graph_uri_encoded = quote_plus(self.graph_uri)
        request_uri = '/_query/q/_result?g={0}'.format(graph_uri_encoded)
        response = self.fetch(request_uri)

        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(expected_response, result)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_get_query_result_with_missing_param(self, mocked_lang):
        request_uri = '/_query/q/_result'
        response = self.fetch(request_uri)
        self.assertEqual(response.code, 400)
        computed = json.loads(response.body)['errors'][0]
        expected = "HTTP error: 400\nMissing key 'g' in querystring.\n  Template: SELECT ?s FROM <%(g)s> {?s a owl:Class}"
        self.assertEqual(computed, expected)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_get_query_result_with_query_not_found(self, mocked_lang):
        self.delete_index()
        request_uri = '/_query/q/_result'
        response = self.fetch(request_uri)
        self.assertEqual(response.code, 404)
        computed = json.loads(response.body)['errors'][0]
        expected = "HTTP error: 404\nThe stored query with id 'q' was not found during execution attempt"
        self.assertEqual(computed, expected)


class StoredQueryWithOptionalsCRUDExecution(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    fixtures = ["tests/sample/gender.n3"]
    graph_uri = "http://example.onto/"

    def setUp(self):
        TornadoAsyncHTTPTestCase.setUp(self)
        self._delete_stored_query()
        request_uri = "/_query/1"
        body = {
            "sparql_template": """
                PREFIX person: <http://test.com/person/>
                PREFIX gender: <http://test.com/person/Gender/>
                SELECT ?s ?label FROM <http://example.onto/> {
                  ?s a person:Gender .
                  OPTIONAL {
                    ?s rdfs:label ?label
                    FILTER(langMatches(lang(?label), "en"))
                  }
                }
            """,
            "description": ""
        }
        body = json.dumps(body)
        response = self.fetch(request_uri, method="PUT", body=body, headers=CLIENT_ID_HEADERS)
        self.assertEqual(response.code, 201)

    def tearDown(self):
        self._delete_stored_query()
        super(StoredQueryWithOptionalsCRUDExecution, self).tearDown()

    def _get_stored_query(self):
        request_uri = "/_query/1"
        response = self.fetch(request_uri)
        return response.code

    def _delete_stored_query(self):
        status = self._get_stored_query()
        if status == 200:
            request_uri = "/_query/1"
            response = self.fetch(request_uri, method="DELETE", headers=CLIENT_ID_HEADERS)
            self.assertEqual(response.code, 204)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_get_query_result_with_optionals(self, mocked_lang):
        expected_response_items = [{
            u"s": u"http://test.com/person/Gender/Male",
            u"label": "Male"
        }, {
            u"s": u"http://test.com/person/Gender/Female",
            u"label": "Female"
        }, {
            u"s": u"http://test.com/person/Gender/Transgender",
            u"label": "Transgender"
        },
            {u"s": u"http://test.com/other_prefix/Test"},
            {u"s": u"http://test.com/person/Gender/Alien"}]

        request_uri = '/_query/1/_result?lang=pt'
        response = self.fetch(request_uri)
        self.assertEqual(response.code, 200)
        result_items = json.loads(response.body)["items"]
        self.assertEqual(sorted(expected_response_items),
                         sorted(result_items))
