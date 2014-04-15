from unittest import TestCase
from mock import patch

from brainiak.stored_query import collection


class StoredQueryCollectionTestCase(TestCase):

    SEARCH_RESULT_2_ITEMS = {"hits": {"hits": [{"_score": 1.0, "_type": "query", "_id": "test1", "fields": {"sparql_template": "", "description": ""}, "_index": "brainiak"}, {"_score": 1.0, "_type": "query", "_id": "test2", "fields": {"sparql_template": "", "description": ""}, "_index": "brainiak"}], "total": 2, "max_score": 1.0}, "_shards": {"successful": 5, "failed": 0, "total": 5}, "took": 1, "timed_out": False}

    def test_get_items_dict(self):
        expected_items = {
            "items": [
                {
                    "resource_id": "test1",
                    "sparql_template": "",
                    "description": ""
                }, {
                    "resource_id": "test2",
                    "sparql_template": "",
                    "description": ""
                }
            ]
        }
        expected_total = 2
        total, items = collection._get_items_dict(self.SEARCH_RESULT_2_ITEMS)
        self.assertEqual(expected_items, items)
        self.assertEqual(expected_total, total)

    @patch("brainiak.stored_query.collection.decorate_dict_with_pagination")
    @patch("brainiak.stored_query.collection._get_items_dict",
           return_value=(1, {"items": [{"sparql_template": "", "description": ""}]}))
    def test_get_response_dict(self, mock_get_items, mock_pagination):
        collection._get_response_dict({"stored_query_result"}, {"params"})
        self.assertTrue(mock_pagination.called)

    @patch("brainiak.stored_query.collection.decorate_dict_with_pagination")
    @patch("brainiak.stored_query.collection._get_items_dict",
           return_value=(0, {"items": []}))
    def test_get_response_dict_with_no_items(self, mock_get_items, mock_pagination):
        response = collection._get_response_dict({"stored_query_result"}, {"params"})
        self.assertTrue("warning" in response)
        self.assertFalse(mock_pagination.called)
