from mock import patch

from tests.tornado_cases import TornadoAsyncHTTPTestCase

import ujson as json


class StoredQueryCRUDIntegrationTestCase(TornadoAsyncHTTPTestCase):

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_put_with_invalid_json(self, mocked_lang):
        response = self.fetch('/_query/my_query_id',
                              method='PUT',
                              body='invalid_json')
        self.assertEqual(response.code, 400)
        self.assertTrue("JSON malformed" in response.body)

    @patch("brainiak.utils.i18n.settings", DEFAULT_LANG="en")
    def test_put_with_json_with_incorrect_schema(self, mocked_lang):
        PAYLOAD_WITHOUT_DESCRIPTION = {
            "sparql_template": "select ?a {?a a owl:Class}"
        }
        response = self.fetch('/_query/my_query_id',
                              method='PUT',
                              body=json.dumps(PAYLOAD_WITHOUT_DESCRIPTION))
        self.assertEqual(response.code, 400)
        self.assertTrue("JSON not according to JSON schema definition", response.body)

    def test_put_create_stored_query(self):
        response = self.fetch('/_query/')
