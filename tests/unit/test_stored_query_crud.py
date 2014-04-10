from unittest import TestCase

from mock import patch

from brainiak.stored_query import crud


class StoredQueryCRUDTestCase(TestCase):

    @patch("brainiak.stored_query.crud.save_instance")
    @patch("brainiak.stored_query.crud.stored_query_exists",
           return_value=True)
    def test_store_query_creation(self,
                                  mock_stored_query_exists,
                                  mock_save_instance):
        expected_response = 200
        entry = {
            "sparql_template": "select ?class {?class a owl:Class}",
            "description": "get all classes _o/"
        }
        query_id = "get_all_classes_query"
        response = crud.store_query(entry, query_id)
        self.assertEqual(response, expected_response)

    @patch("brainiak.stored_query.crud.save_instance")
    @patch("brainiak.stored_query.crud.stored_query_exists",
           return_value=False)
    def test_store_query_edition(self,
                                 mock_stored_query_exists,
                                 mock_save_instance):
        expected_response = 201
        entry = {
            "sparql_template": "select ?class from <%(graph_uri)s> {?class a owl:Class}",
            "description": "get all classes with graph_uri as parameter"
        }
        query_id = "get_all_classes_query"
        response = crud.store_query(entry, query_id)
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

    @patch("brainiak.stored_query.crud.delete_instance",
           return_value=True)
    def test_delete_stored_query_that_exists(self, mock_delete):
        query_id = "existent_query"
        self.assertTrue(crud.delete_stored_query(query_id))

    @patch("brainiak.stored_query.crud.delete_instance",
           return_value=False)
    def test_delete_stored_query_but_does_not_exist(self, mock_delete):
        query_id = "existent_query"
        self.assertFalse(crud.delete_stored_query(query_id))

    @patch("brainiak.stored_query.crud.get_stored_query", return_value={})
    def test_stored_query_exists(self, mocked_get_stored_query):
        self.assertTrue(crud.stored_query_exists("query_id"))

    @patch("brainiak.stored_query.crud.get_stored_query", return_value=None)
    def test_stored_query_does_not_exist(self, mocked_get_stored_query):
        self.assertFalse(crud.stored_query_exists("query_id"))
