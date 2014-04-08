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


    def _query_exists(self, query_id):
        response = self.fetch('/_query/{0}'.format(query_id),
                              method='GET')
        return response.code != 404

    def _assert_query_does_not_exist(self, query_id):
        if self._query_exists(query_id):
            self.fail("Query exists")

    def _assert_query_exists(self, query_id):
        if not self._query_exists(query_id):
            self.fail("Query should exist")

    def test_put_create_stored_query(self):
        query_id = "my_test_query"
        self._assert_query_does_not_exist(query_id)

        entry = '''{
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "my query"
        }'''

        create_response = self.fetch('/_query/{0}'.format(query_id),
                              method='PUT',
                              body=entry)
        self.assertEqual(create_response.code, 201)

        self._assert_query_exists(query_id)

        # delete inserted query
        delete_response = self.fetch('/_query/{0}'.format(query_id),
                      method='DELETE')
        self.assertEqual(delete_response.code, 204)

    def test_put_edit_stored_query(self):
        query_id = "my_test_query"
        self._assert_query_does_not_exist(query_id)

        entry = '''{
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "my query"
        }'''

        create_response = self.fetch('/_query/{0}'.format(query_id),
                              method='PUT',
                              body=entry)
        self.assertEqual(create_response.code, 201)

        self._assert_query_exists(query_id)

        modified_entry = '''{
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "my modified query"
        }'''

        expected_code = 200
        edit_response = self.fetch('/_query/{0}'.format(query_id),
                              method='PUT',
                              body=modified_entry)
        self.assertEqual(edit_response.code, expected_code)

        expected_description = "my modified query"
        get_response = self.fetch('/_query/{0}'.format(query_id),
                              method='GET')
        new_description = json.loads(get_response.body)["description"]
        self.assertEqual(new_description, expected_description)

        # delete inserted query
        delete_response = self.fetch('/_query/{0}'.format(query_id),
                      method='DELETE')
        self.assertEqual(delete_response.code, 204)

    def test_get_stored_query_that_does_not_exist(self):
        query_id = "my_inexistent_query_id"
        self.assertFalse(self._query_exists(query_id))

    def test_get_stored_query_exists(self):
        query_id = "my_test_query"
        self._assert_query_does_not_exist(query_id)

        entry = '''{
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "my query"
        }'''

        create_response = self.fetch('/_query/{0}'.format(query_id),
                              method='PUT',
                              body=entry)
        self.assertEqual(create_response.code, 201)

        self._assert_query_exists(query_id)

        # delete inserted query
        delete_response = self.fetch('/_query/{0}'.format(query_id),
                      method='DELETE')
        self.assertEqual(delete_response.code, 204)

    def test_delete_that_does_not_exist(self):
        query_id = "my_inexistent_query_id"
        self._assert_query_does_not_exist(query_id)

        delete_response = self.fetch('/_query/{0}'.format(query_id),
                      method='DELETE')
        self.assertEqual(delete_response.code, 404)


    def test_delete_stored_query_exists(self):
        query_id = "my_test_query"
        self._assert_query_does_not_exist(query_id)

        entry = '''{
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "my query"
        }'''

        create_response = self.fetch('/_query/{0}'.format(query_id),
                              method='PUT',
                              body=entry)
        self.assertEqual(create_response.code, 201)

        self._assert_query_exists(query_id)

        # delete inserted query
        delete_response = self.fetch('/_query/{0}'.format(query_id),
                      method='DELETE')
        self.assertEqual(delete_response.code, 204)
