from unittest import TestCase

from tornado.web import HTTPError
from mock import patch

from brainiak.stored_query import crud


class StoredQueryCRUDTestCase(TestCase):

    @patch("brainiak.stored_query.crud.save_instance")
    @patch("brainiak.stored_query.crud.get_stored_query",
           return_value={"client_id": "client_id"})
    @patch("brainiak.stored_query.crud._allowed_query",
           return_value=True)
    def test_store_query_creation(self,
                                  mock_allowed,
                                  mock_stored_query_exists,
                                  mock_save_instance):
        expected_response = 200
        entry = {
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "get all classes _o/"
        }
        query_id, client_id = "get_all_classes_query", "client_id"
        response = crud.store_query(entry, query_id, client_id)
        self.assertEqual(response, expected_response)

    @patch("brainiak.stored_query.crud.save_instance")
    @patch("brainiak.stored_query.crud.get_stored_query",
           return_value=None)
    @patch("brainiak.stored_query.crud._allowed_query",
           return_value=True)
    def test_store_query_edition(self,
                                 mock_allowed,
                                 mock_stored_query_exists,
                                 mock_save_instance):
        expected_response = 201
        entry = {
            "sparql_template": "select ?class from <%(graph_uri)s> {?class a owl:Class}",
            "description": "get all classes with graph_uri as parameter"
        }
        query_id, client_id = "get_all_classes_query", "client_id"
        response = crud.store_query(entry, query_id, client_id)
        self.assertEqual(response, expected_response)

    def test_get_stored_query(self):
        query_example = {
            "_source": {
                "sparql_template": "",
                "description": ""
            }
        }
        query_id = "my_query_id"
        with patch("brainiak.stored_query.crud.get_instance",
                   return_value=query_example):
            response = crud.get_stored_query(query_id)
            self.assertEqual(response, query_example["_source"])

    @patch("brainiak.stored_query.crud.get_instance",
           return_value=None)
    def test_get_stored_query_is_none(self, mocked_get_instance):
        query_id = "query_id"
        response = crud.get_stored_query(query_id)
        self.assertEqual(response, None)

    @patch("brainiak.stored_query.crud.get_stored_query",
           return_value=None)
    def test_stored_query_exists_but_it_does_not(self, mock_get_stored_query):
        query_id = "non_existent_query"
        self.assertFalse(crud.stored_query_exists(query_id))

    @patch("brainiak.stored_query.crud.get_stored_query",
           return_value={})
    def test_stored_query_exists_but_it_does(self, mock_get_stored_query):
        query_id = "existent_query"
        self.assertTrue(crud.stored_query_exists(query_id))

    @patch("brainiak.stored_query.crud.validate_client_id")
    @patch("brainiak.stored_query.crud.get_stored_query", return_value={"client_id": "client_id"})
    @patch("brainiak.stored_query.crud.delete_instance")
    def test_delete_stored_query_that_exists(self, mock_delete, mock_get_stored_query, mock_validate_client_id):
        query_id = "existent_query"
        client_id = "client_id"
        self.assertIsNone(crud.delete_stored_query(query_id, client_id))

    @patch("brainiak.stored_query.crud.get_stored_query", return_value=None)
    def test_delete_inexistent_stored_query_raises_error(self, mock_delete):
        query_id = "existent_query"
        client_id = "client_id"
        self.assertRaises(HTTPError, crud.delete_stored_query, query_id, client_id)

    @patch("brainiak.stored_query.crud.get_stored_query", return_value={})
    def test_stored_query_exists(self, mocked_get_stored_query):
        self.assertTrue(crud.stored_query_exists("query_id"))

    @patch("brainiak.stored_query.crud.get_stored_query", return_value=None)
    def test_stored_query_does_not_exist(self, mocked_get_stored_query):
        self.assertFalse(crud.stored_query_exists("query_id"))

    def test_valid_query_for_invalid_query(self):
        query_template = """
        INSERT DATA INTO <xubi> {
          <1> <2> <3>
        }
        """
        response = crud._allowed_query(query_template)
        self.assertFalse(response)

    def test_valid_query_for_invalid_query_2(self):
        query_template = """INSERT DATA INTO <xubi> {
          <1> <2> <3>
        }
        """
        response = crud._allowed_query(query_template)
        self.assertFalse(response)

    def test_valid_query_for_invalid_query_with_comment_block(self):
        query_template = """/*aaa*/INSERT DATA INTO <xubi> {
          <1> <2> <3>
        }
        """
        response = crud._allowed_query(query_template)
        self.assertFalse(response)

    def test_valid_query(self):
        query_template = """
        SELECT * {
          <1> insert:xubiru ?modify
        }
        """
        response = crud._allowed_query(query_template)
        self.assertTrue(response)

    def test_valid_query_for_with_comment_block(self):
        query_template = """
        /*INSERT comment modify */SELECT * {
          <1> insert:xubiru ?modify
        }
        """
        response = crud._allowed_query(query_template)
        self.assertTrue(response)

    @patch("brainiak.stored_query.crud._allowed_query",
           return_value=False)
    def test_not_allowed_query_raises_error(self, mock_allowed):
        entry = {
            "sparql_template": "INSERT DATA INTO <a> {<1> <2> <3>}"
        }
        query_id, client_id = "query_id", "client_id"
        self.assertRaises(HTTPError, crud.store_query, entry, query_id, client_id)

    def test_headers_with_client_id(self):
        crud.validate_headers({"X-Brainiak-Client-Id": "dsd4asdr6aftsg7asgdsa"})

    def test_headers_without_client_id_raises_exception(self):
        self.assertRaises(HTTPError, crud.validate_headers, {"a-header": "a-value"})

    def test_validate_client_id(self):
        client_id = "client_id"
        stored_query = {"client_id": "client_id"}
        self.assertIsNone(crud.validate_client_id(client_id, stored_query))

    def test_validate_client_id_raises_exception(self):
        client_id = "other_client_id"
        stored_query = {"client_id": "client_id"}
        self.assertRaises(HTTPError, crud.validate_client_id, client_id, stored_query)
