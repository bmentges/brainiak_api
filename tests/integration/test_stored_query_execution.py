from mock import patch
from urllib import quote_plus

from tests.sparql import QueryTestCase
from tests.tornado_cases import TornadoAsyncHTTPTestCase

import ujson as json


class StoredQueryCRUDExecution(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    fixtures = ["tests/sample/gender.n3"]
    graph_uri = "http://example.onto/"

    query_id = "my_integration_test_query_id"

    def setUp(self):
        super(TornadoAsyncHTTPTestCase, self).setUp()
        request_uri = "/_query/{0}".format(self.query_id)
        body = '''{
            "sparql_template": "SELECT ?s FROM <%(g)s> {?s a owl:Class}",
            "description": ""
        }'''
        response = self.fetch(request_uri, method="PUT", body=body)
        # 200,201: dont worry if test fails and tearDown is not called to delete the query
        self.assertTrue(response.code in (200,201))

    def tearDown(self):
        super(TornadoAsyncHTTPTestCase, self).setUp()
        request_uri = "/_query/{0}".format(self.query_id)
        response = self.fetch(request_uri, method="DELETE")
        self.assertEqual(response.code, 204)


    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_get_query_result(self, mocked_lang):
        expected_response = {
            u"items": [{u"s": u"http://test.com/person/Gender"}]
        }

        graph_uri_encoded = quote_plus(self.graph_uri)
        request_uri = '/_query/{0}/_result?g={1}'.format(self.query_id,
                                                         graph_uri_encoded)
        response = self.fetch(request_uri)

        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(expected_response, result)
