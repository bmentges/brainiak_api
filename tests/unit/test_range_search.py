from unittest import TestCase

from mock import patch

from tornado.web import HTTPError

from brainiak.range_search.range_search import _build_body_query, _validate_class_restriction, \
    _validate_graph_restriction, _build_type_filters, _graph_uri_to_index_name, \
    _build_class_label_dict


class RangeSearchTestCase(TestCase):

    @patch("brainiak.range_search.range_search._build_type_filters", return_value={})
    def test_build_query_body(self, mocked_build_type_filters):
        expected = {
            "query": {
                "query_string": {
                    "query": "rio AND de AND jan*"
                }
            },
            "filter": {}
        }

        params = {
            "pattern": "Rio De Jan"
        }

        response = _build_body_query(params, [])
        self.assertEqual(expected, response)

    @patch("brainiak.range_search.range_search.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction(self, mocked_filter_values):
        expected = ["class1"]

        params = {
            "restrict_classes": ["class1"]
        }

        response = _validate_class_restriction(params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.range_search.range_search.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["class1", "class2"]

        params = {
            "restrict_classes": None
        }

        response = _validate_class_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.range_search.range_search.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_raises_error(self, mocked_filter_values):
        params = {
            "restrict_classes": ["class1", "class2", "class3"],
            "predicate": "predicate1"
        }
        self.assertRaises(HTTPError, _validate_class_restriction, params, None)  # None because filter_values is mocked

    @patch("brainiak.range_search.range_search.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction(self, mocked_filter_values):
        expected = ["graph1"]

        params = {
            "restrict_graphs": ["graph1"]
        }

        response = _validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.range_search.range_search.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["graph1", "graph2"]

        params = {
            "restrict_graphs": None
        }

        response = _validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.range_search.range_search.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_raises_error(self, mocked_filter_values):
        params = {
            "restrict_graphs": ["graph1", "graph2", "graph3"],
            "predicate": "predicate1"
        }
        self.assertRaises(HTTPError, _validate_graph_restriction, params, None)  # None because filter_values is mocked

    def test_build_type_filters(self):
        expected = {
            "or": [
                {
                    "type": {
                        "value": "http://semantica.globo.com/base/Pessoa"
                    }
                },
                {
                    "type": {
                        "value": "http://semantica.globo.com/place/City"
                    }
                }
            ]
        }
        classes = ["http://semantica.globo.com/base/Pessoa", "http://semantica.globo.com/place/City"]

        response = _build_type_filters(classes)
        self.assertEqual(expected, response)

    def test_graph_uri_to_index_name_base(self):
        graph_uri = "http://semantica.globo.com/"
        expected = "semantica.glb"
        result = _graph_uri_to_index_name(graph_uri)
        self.assertEqual(result, expected)

    def test_graph_uri_to_index_name_place(self):
        graph_uri = "http://semantica.globo.com/place/"
        expected = "semantica.place"
        result = _graph_uri_to_index_name(graph_uri)
        self.assertEqual(result, expected)

    def test_build_class_label_dict(self):
        expected = {
            "class1": "label1",
            "class2": "label2"
        }
        compressed_result = [
            {
                "range": "class1",
                "range_graph": "graph1",
                "range_label": "label1"
            },
            {
                "range": "class2",
                "range_graph": "graph2",
                "range_label": "label2"
            }
        ]
        response = _build_class_label_dict(compressed_result)
        self.assertEqual(expected, response)
