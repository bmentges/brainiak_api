from unittest import TestCase

from mock import patch

from tornado.web import HTTPError

from brainiak.suggest import suggest


class SuggestTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None

    @patch("brainiak.suggest.suggest._build_type_filters", return_value={})
    @patch("brainiak.suggest.suggest.calculate_offset", return_value=10)
    def test_build_query_body(self, mocked_calculate_offset, mocked_build_type_filters):

        query_params = {
            "page": "1"
        }
        search_params = {
            "pattern": "Rio De Jan",
        }
        classes = []
        search_fields = ["rdfs:label", "upper:name"]
        response_fields = ["upper:name"]

        response = suggest._build_body_query(query_params, search_params, classes, search_fields, response_fields)

        expected = {
            'filter': {},
            'fields': ['upper:name'],
            'query': {
                'bool': {
                    'should': {
                        'query_string': {
                            'fields': ['rdfs:label', 'upper:name'],
                            'analyze_wildcard': True,
                            'query': '"rio AND de AND jan*"'
                        }
                    },
                    'must': {
                        'query_string': {
                            'fields': ['rdfs:label', 'upper:name'],
                            'analyze_wildcard': True,
                            'query': 'rio AND de AND jan*'
                        }
                    }
                }
            },
            'from': 10,
            'size': 10
        }

        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction(self, mocked_filter_values):
        expected = ["class1"]

        search_params = {
            "classes": ["class1"]
        }

        response = suggest._validate_class_restriction(search_params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["class1", "class2"]

        params = {}

        response = suggest._validate_class_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.suggest.suggest.filter_values", return_value=["class1", "class2"])
    def test_validate_classes_restriction_raises_error(self, mocked_filter_values):
        params = {
            "classes": ["class1", "class2", "class3"],
            "target": "predicate1"
        }
        self.assertRaises(HTTPError, suggest._validate_class_restriction, params, None)  # None because filter_values is mocked

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction(self, mocked_filter_values):
        expected = ["graph1"]

        params = {
            "graphs": ["graph1"]
        }

        response = suggest._validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_with_no_restriction_param(self, mocked_filter_values):
        expected = ["graph1", "graph2"]

        params = {}

        response = suggest._validate_graph_restriction(params, None)  # None because filter_values is mocked
        self.assertListEqual(sorted(expected), sorted(response))

    @patch("brainiak.suggest.suggest.filter_values", return_value=["graph1", "graph2"])
    def test_validate_graphs_restriction_raises_error(self, mocked_filter_values):
        expected_message = "Classes in the range of predicate 'predicate1' are not in graphs ['graph3']"
        params = {
            "graphs": ["graph1", "graph2", "graph3"],
            "target": "predicate1"
        }
        try:
            suggest._validate_graph_restriction(params, None)  # None because filter_values is mocked
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
            suggest._validate_graph_restriction(params, None)  # None because filter_values is mocked
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

        response = suggest._build_type_filters(classes)
        self.assertEqual(expected, response)

    def test_build_class_label_and_graph_dict(self):
        class_label_dict = {
            "class1": "label1",
            "class2": "label2"
        }
        class_graph_dict = {
            "class1": "graph1",
            "class2": "graph2"
        }

        expected = class_label_dict, class_graph_dict

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
        response = suggest._build_class_label_and_class_graph_dicts(compressed_result)
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest.get_instance_class_schema", return_value={})
    @patch("brainiak.suggest.suggest._get_class_fields_to_response", return_value={})
    @patch("brainiak.suggest.suggest.get_instance_fields", return_value={})
    @patch("brainiak.suggest.suggest._get_title_value", return_value=("rdfs:label", "Globoland"))
    def test_build_items(self, mocked_get_title_value,
                         mocked_get_instance_fields, mocked_get_class_fields_to_response,
                         mock_get_instance_class_schema):
        elasticsearch_result = {
            "hits": {
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
        query_params = []  # needed to get_instance_fields, mocked
        required_fields = []  # needed to get_instance_fields, mocked
        response_fields_by_class = {}  # needed to get_instance_fields, mocked
        class_fields = []  # needed to _get_class_fields_to_response, mocked

        computed = suggest._build_items(query_params, elasticsearch_result,
                                                  class_label_dict, title_fields,
                                                  response_fields_by_class,
                                                  class_fields, required_fields)
        expected = {
            "@id": "http://semantica.globo.com/place/City/9d9e1ae6-a02f-4c2e-84d3-4219bf9d243a",
            "title": "Globoland",
            "@type": "http://semantica.globo.com/place/City",
            "type_title": "Cidade",
        }

        self.assertEqual(len(computed), 1)
        self.assertDictEqual(expected, computed[0])

    @patch("brainiak.suggest.suggest._get_subproperties", return_value=["property1", "property2"])
    def test_get_search_fields(self, mocked_get_subproperties):
        expected = {"property1", "property2", "rdfs:label"}
        search_params = {
            "fields": ["rdfs:label"]
        }
        search_fields = suggest._get_search_fields({}, search_params)

        self.assertEqual(expected, set(search_fields))

    def test_get_title_value(self):
        expected = ("rdfs:label", "label1")
        elasticsearch_fields = {
            "rdfs:label": "label1",
            "upper:name": "label2"
        }
        title_fields = ["upper:name", "rdfs:label"]

        response = suggest._get_title_value(elasticsearch_fields, title_fields)
        self.assertEqual(expected, response)

    def test_get_title_value_raises_exception(self):
        elasticsearch_fields = {
            "rdfs:label": "label1",
            "upper:name": "label2"
        }
        title_fields = ["unexistent:name"]

        self.assertRaises(RuntimeError, suggest._get_title_value, elasticsearch_fields, title_fields)

    def test_build_class_fields_query(self):
        expected = """
SELECT DISTINCT ?field_value {
  ?s <field> ?field_value
  FILTER(?s = <class_a> OR ?s = <class_b>)
}
"""
        classes = ["class_a", "class_b"]
        meta_field = "field"
        self.assertEqual(expected, suggest._build_class_fields_query(classes, meta_field))

    @patch("brainiak.suggest.suggest._get_class_fields_value",
           return_value=["metafield1, metafield2", "metafield2", "metafield2, metafield3"])
    def test_get_response_fields_from_meta_fields(self, mocked_get_meta_fields_value):
        expected = ["metafield3", "metafield2", "metafield1"]
        response_params = {
            "meta_fields": ["a", "b"]
        }
        query_params = classes = {}
        response = suggest._get_response_fields_from_meta_fields(query_params, response_params, classes)
        self.assertEqual(sorted(expected), sorted(response))

    ##################################
    # get_instance_fields

    def test_get_instance_fields_for_not_required_object_property(self):
        class_schema = {
            "properties": {
                "http://predicate2": {"title": "predicate2_title"}
            }
        }
        elastic_search_item = {
            "fields": {
                "http://predicate2": {
                    "title": "predicate2_value_label",
                    "@id": "http://predicate2_value"
                }
            }
        }
        computed = suggest.get_instance_fields(elastic_search_item, class_schema)
        expected = [
            {
                "predicate_id": "http://predicate2",
                "predicate_title": "predicate2_title",
                "object_id": "http://predicate2_value",
                "object_title": "predicate2_value_label",
                "required": False
            }
        ]
        self.assertEqual(computed, expected)

    def test_get_instance_fields_for_property_with_multiple_objects(self):
        class_schema = {
            "properties": {
                ":hasParent": {
                    "title": "Father or mother"
                },
            }
        }
        elastic_search_item = {
            "fields": {":hasParent": ["Marry", "Harry"]}
        }
        computed = suggest.get_instance_fields(elastic_search_item, class_schema)
        expected = [
            {
                "predicate_id": ":hasParent",
                "predicate_title": "Father or mother",
                "object_title": "Marry",
                "required": False
            },
            {
                "predicate_id": ":hasParent",
                "predicate_title": "Father or mother",
                "object_title": "Harry",
                "required": False
            }
        ]
        self.assertEqual(computed, expected)

    def test_get_instance_fields_for_required_datatype_property(self):
        class_schema = {
            "properties": {
                "http://predicate1": {
                    "title": "predicate1_title",
                    "required": True
                },
            }
        }
        elastic_search_item = {
            "fields": {"http://predicate1": "predicate1_value"}
        }
        computed = suggest.get_instance_fields(elastic_search_item, class_schema)
        expected = [
            {
                "predicate_id": "http://predicate1",
                "predicate_title": "predicate1_title",
                "object_title": "predicate1_value",
                "required": True
            }
        ]
        self.assertEqual(computed, expected)

    def test_get_instance_fields_for_multiple_fields(self):
        class_schema = {
            "properties": {
                ":atContry": {"title": "Place is inside country"},
                ":hasMainLanguage": {"title": "Most common language in place"}
            }
        }
        elastic_search_item = {
            "fields": {
                ":atContry": "Peru",
                ":hasMainLanguage": "Spanish"
            }
        }
        computed = suggest.get_instance_fields(elastic_search_item, class_schema)
        expected = [
            {
                "predicate_id": ":hasMainLanguage",
                "predicate_title": "Most common language in place",
                "object_title": "Spanish",
                "required": False
            },
            {
                "predicate_id": ":atContry",
                "predicate_title": "Place is inside country",
                "object_title": "Peru",
                "required": False
            }
        ]
        self.assertEqual(computed, expected)

    ##################################

    def test_remove_title_field_removes_existing_title_property(self):
        elastic_search_item = {
            "fields": {
                ":name": "Cuzco",
                ":atContry": "Peru",
                ":hasMainLanguage": "Spanish"
            }
        }
        title_field = ":name"
        suggest.remove_title_field(elastic_search_item, title_field)
        expected = {
            "fields": {
                ":atContry": "Peru",
                ":hasMainLanguage": "Spanish"
            }
        }
        self.assertEqual(elastic_search_item, expected)

    def test_remove_title_field_does_not_remove_existing_title_property(self):
        elastic_search_item = {
            "fields": {
                ":atContry": "Brazil",
                ":hasMainLanguage": "Portuguese"
            }
        }
        title_field = ":name"
        suggest.remove_title_field(elastic_search_item, title_field)
        expected = {
            "fields": {
                ":atContry": "Brazil",
                ":hasMainLanguage": "Portuguese"
            }
        }
        self.assertEqual(elastic_search_item, expected)

    ##################################

    # def test_get_instance_fields_only_title_field(self):
    #     expected = {}
    #     query_params = {}
    #     instance_uri = "instance-uri"
    #     klass = "klass"
    #     title_field = "http://predicate3"
    #     required_fields = []
    #     response_fields_by_class = {"klass": ["http://predicate3"]}

    #     instance_fields = suggest.get_instance_fields(query_params, instance_uri,
    #                                            klass, title_field,
    #                                            response_fields_by_class,
    #                                            required_fields)
    #     self.assertDictEqual(expected, instance_fields)

    def test_get_response_fields_from_classes_dict(self):
        expected_dict_type1 = ["field1", "field2", "field4"]
        expected_dict_type2 = ["field2", "field3", "field4"]
        expected_dict_type3 = ["field4"]

        expected_set = set(["field1", "field2", "field3"])
        response_fields = set(["field4"])
        classes = ["type1", "type2", "type3"]

        fields_by_class_list = [
            {
                "@type": "type1",
                "instance_fields": ["field1", "field2"]
            },
            {
                "@type": "type2",
                "instance_fields": ["field2", "field3"]
            }
        ]

        response_dict, response_set = suggest._get_response_fields_from_classes_dict(fields_by_class_list, response_fields, classes)
        self.assertEqual(sorted(response_dict["type1"]), sorted(expected_dict_type1))
        self.assertEqual(sorted(response_dict["type2"]), sorted(expected_dict_type2))
        self.assertEqual(sorted(response_dict["type3"]), sorted(expected_dict_type3))
        self.assertEqual(expected_set, response_set)

    def test_get_response_fields_from_classes_dict_empty(self):
        expected_dict = {
            "type": ["field1"]
        }
        expected_set = set([])
        response_fields = set(["field1"])
        classes = ["type"]

        fields_by_class_list = []

        response_dict, response_set = suggest._get_response_fields_from_classes_dict(fields_by_class_list,
                                                                             response_fields, classes)
        self.assertEqual(expected_dict, response_dict)
        self.assertEqual(expected_set, response_set)

    @patch("brainiak.suggest.suggest._get_class_fields_value", return_value=["value1"])
    def test_get_class_fields_to_response(self, mocked_get_class_fields_value):
        expected = {
            "class_fields": {
                "field1": "value1"
            }
        }
        query_params = {}  # needed to _get_class_fields_value mocked
        classes = []  # needed to _get_class_fields_value mocked
        class_fields = ["field1"]

        response = suggest._get_class_fields_to_response(query_params, classes, class_fields)
        self.assertEqual(expected, response)

    @patch("brainiak.suggest.suggest._get_class_fields_value", return_value=[])
    def test_get_class_fields_to_response_no_value(self, mocked_get_class_fields_value):
        expected = {}
        query_params = {}  # needed to _get_class_fields_value mocked
        classes = []  # needed to _get_class_fields_value mocked
        class_fields = ["field1"]

        response = suggest._get_class_fields_to_response(query_params, classes, class_fields)
        self.assertEqual(expected, response)

    def test_get_required_fields_from_schema_response(self):
        expected = ["prop2"]
        schema = {
            "properties": {
                "prop1": {
                    "graph": "",
                    "range": ""
                },
                "prop2": {
                    "graph": "",
                    "range": "",
                    "required": True
                }
            }
        }
        response = suggest._get_required_fields_from_schema_response(schema)
        self.assertEqual(expected, response)
