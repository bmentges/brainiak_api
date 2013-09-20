from unittest import TestCase

from mock import patch

from tornado.web import HTTPError

from brainiak.suggest.suggest import _build_body_query, _validate_class_restriction, \
    _validate_graph_restriction, _build_type_filters, _graph_uri_to_index_name, \
    _build_class_label_dict, _build_items, _get_search_fields, _get_title_value, \
    _build_meta_fields_query, _get_response_fields_from_meta_fields, \
    _build_predicate_values_query, _get_instance_fields


class SuggestTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None

    @patch("brainiak.suggest.suggest._build_type_filters", return_value={})
    @patch("brainiak.suggest.suggest.calculate_offset", return_value=10)
    def test_build_query_body(self, mocked_calculate_offset, mocked_build_type_filters):
        expected = {
            "from": 10,
            "size": 10,
            "fields": ["upper:name"],
            "query": {
                "query_string": {
                    "query": "rio AND de AND jan*",
                    "fields": ["rdfs:label", "upper:name"],
                }
            },
            "filter": {}
        }

        query_params = {
            "page": "1"
        }
        search_params = {
            "pattern": "Rio De Jan",
        }
        classes = []
        search_fields = ["rdfs:label", "upper:name"]
        response_fields = ["upper:name"]

        response = _build_body_query(query_params, search_params, classes, search_fields, response_fields)
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction(self, mocked_filter_values):
        expected = ["class1"]

        search_params = {
            "classes": ["class1"]
        }

        response = _validate_class_restriction(search_params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["class1", "class2"]

        params = {}

        response = _validate_class_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_raises_error(self, mocked_filter_values):
        params = {
            "classes": ["class1", "class2", "class3"],
            "target": "predicate1"
        }
        self.assertRaises(HTTPError, _validate_class_restriction, params, None)  # None because filter_values is mocked

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction(self, mocked_filter_values):
        expected = ["graph1"]

        params = {
            "graphs": ["graph1"]
        }

        response = _validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["graph1", "graph2"]

        params = {}

        response = _validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_raises_error(self, mocked_filter_values):
        expected_message = "Classes in the range of predicate 'predicate1' are not in graphs ['graph3']"
        params = {
            "graphs": ["graph1", "graph2", "graph3"],
            "target": "predicate1"
        }
        try:
            _validate_graph_restriction(params, None)  # None because filter_values is mocked
        except HTTPError as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(e.log_message, expected_message)
        else:
            self.fail("a HTTPError should be raised")

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph_without_instances1", "graph_without_instances2"])
    @patch("brainiak.suggest.suggest.settings", GRAPHS_WITHOUT_INSTANCES=["graph_without_instances1", "graph_without_instances2"])
    def test_validate_graphs_restriction_raises_error_for_graphs_without_instances(self, mocked_settings, mocked_filter_values):
        expected_message = "Classes in the range of predicate 'predicate1' are in graphs without instances," + \
            " such as: ['graph_without_instances1', 'graph_without_instances2']"
        params = {
            "target": "predicate1"
        }
        try:
            _validate_graph_restriction(params, None)  # None because filter_values is mocked
        except HTTPError as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(e.log_message, expected_message)
        else:
            self.fail("a HTTPError should be raised")

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

    @patch("brainiak.suggest.suggest._get_instance_fields", return_value={})
    @patch("brainiak.suggest.suggest._get_title_value", return_value=("rdfs:label", "Globoland"))
    def test_build_items(self, mocked_get_title_value, mocked_get_instance_fields):
        expected = {
            "@id": "http://semantica.globo.com/place/City/9d9e1ae6-a02f-4c2e-84d3-4219bf9d243a",
            "title": "Globoland",
            "@type": "http://semantica.globo.com/place/City",
            "type_title": "Cidade",
        }

        elasticsearch_result = {
            "took": 256,
            "timed_out": False,
            "_shards": {
                "total": 109,
                "successful": 109,
                "failed": 0
            },
            "hits": {
                "total": 1,
                "max_score": 1,
                "hits": [
                    {
                        "_index": "semantica.place",
                        "_type": "http://semantica.globo.com/place/City",
                        "_id": "http://semantica.globo.com/place/City/9d9e1ae6-a02f-4c2e-84d3-4219bf9d243a",
                        "_score": 1,
                        "fields": {
                            "rdfs:label": "Globoland"
                        }
                    }
                ]
            }
        }

        class_label_dict = {
            "http://semantica.globo.com/place/City": "Cidade"
        }
        title_fields = []  # mocked _get_title_value
        response_fields = []  # mocked _get_instance_fields
        query_params = []  # needed to _get_instance_fields, mocked

        items_response, item_count = _build_items(
            query_params, elasticsearch_result, class_label_dict, title_fields, response_fields)

        self.assertEqual(len(items_response), 1)
        self.assertDictEqual(expected, items_response[0])

    @patch("brainiak.suggest.suggest._get_subproperties", return_value=["property1", "property2"])
    def test_get_search_fields(self, mocked_get_subproperties):
        expected = {"property1", "property2", "rdfs:label"}
        search_params = {
            "fields": ["rdfs:label"]
        }
        search_fields = _get_search_fields({}, search_params)

        self.assertEqual(expected, set(search_fields))

    def test_get_title_value(self):
        expected = ("rdfs:label", "label1")
        elasticsearch_fields = {
            "rdfs:label": "label1",
            "upper:name": "label2"
        }
        title_fields = ["upper:name", "rdfs:label"]

        response = _get_title_value(elasticsearch_fields, title_fields)
        self.assertEqual(expected, response)

    def test_get_title_value_raises_exception(self):
        elasticsearch_fields = {
            "rdfs:label": "label1",
            "upper:name": "label2"
        }
        title_fields = ["unexistent:name"]

        self.assertRaises(RuntimeError, _get_title_value, elasticsearch_fields, title_fields)

    def test_build_meta_fields_query(self):
        expected = """
SELECT DISTINCT ?meta_field_value {
  ?s <meta_field> ?meta_field_value
  FILTER(?s = <class_a> OR ?s = <class_b>)
}
"""
        classes = ["class_a", "class_b"]
        meta_field = "meta_field"
        self.assertEqual(expected, _build_meta_fields_query(classes, meta_field))

    @patch("brainiak.suggest.suggest._get_meta_fields_value",
           return_value=["metafield1, metafield2", "metafield2", "metafield2, metafield3"])
    def test_get_response_fields_from_meta_fields(self, mocked_get_meta_fields_value):
        expected = ["metafield3", "metafield2", "metafield1"]
        response_params = {
            "meta_fields": ["a", "b"]
        }
        query_params = classes = {}
        response = _get_response_fields_from_meta_fields(query_params, response_params, classes)
        self.assertEqual(sorted(expected), sorted(response))

    def test_build_predicate_values_query(self):
        expected = """
SELECT ?object_value ?object_value_label ?predicate ?predicate_title {
  <http://instance-uri> ?predicate ?object_value OPTION(inference "http://semantica.globo.com/ruleset") .
  OPTIONAL { ?object_value rdfs:label ?object_value_label OPTION(inference "http://semantica.globo.com/ruleset") }
  ?predicate rdfs:label ?predicate_title .
  FILTER(?predicate = <http://predicate-a> OR ?predicate = <http://predicate-b>)
}
"""
        instance_uri = "http://instance-uri"
        instance_fields = ["http://predicate-a", "http://predicate-b"]
        self.assertEqual(expected, _build_predicate_values_query(instance_uri, instance_fields))

    @patch("brainiak.suggest.suggest._get_predicate_values", return_value=[
        {
            "predicate": "http://predicate1",
            "predicate_title": "predicate1_title",
            "object_value": "predicate1_value"
        },
        {
            "predicate": "http://predicate2",
            "predicate_title": "predicate2_title",
            "object_value": "http://predicate2_value",
            "object_value_label": "predicate2_value_label"
        }
    ])
    def test_get_instance_fields(self, mocked_get_predicate_values):
        expected = {
            "instance_fields": [
                {
                    "predicate_id": "http://predicate1",
                    "predicate_title": "predicate1_title",
                    "object_title": "predicate1_value"
                },
                {
                    "predicate_id": "http://predicate2",
                    "predicate_title": "predicate2_title",
                    "object_id": "http://predicate2_value",
                    "object_title": "predicate2_value_label"
                }
            ]
        }
        query_params = {}  # mocked
        instance_uri = "instance-uri"
        klass = "klass"
        response_fields = ["http://predicate1", "http://predicate2", "http://predicate3"]
        title_field = "http://predicate3"
        instance_fields = _get_instance_fields(query_params, instance_uri, klass, response_fields, title_field)
        mocked_get_predicate_values.assert_called_with({}, "instance-uri", ["http://predicate1", "http://predicate2"])
        self.assertDictEqual(expected, instance_fields)
