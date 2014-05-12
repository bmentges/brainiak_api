from unittest import TestCase

from mock import patch
from tornado.web import HTTPError

from brainiak.utils.params import ParamDict
from brainiak.suggest import suggest
from tests.mocks import MockHandler


class SuggestTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None

    @patch("brainiak.suggest.suggest._build_type_filters", return_value={})
    @patch("brainiak.suggest.suggest.resources.calculate_offset", return_value=10)
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
                            'analyzer': 'default',
                            'analyze_wildcard': True,
                            'query': '"rio* AND de* AND jan*"'
                        }
                    },
                    'must': {
                        'query_string': {
                            'fields': ['rdfs:label', 'upper:name'],
                            'analyzer': 'default',
                            'analyze_wildcard': True,
                            'query': u'rio* AND de* AND jan*'
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

    @patch("brainiak.suggest.suggest.get_instance_class_schema", return_value={"title": "Cidade"})
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
        title_fields = []  # mocked _get_title_value
        query_params = []  # needed to get_instance_fields, mocked
        class_fields = []  # needed to _get_class_fields_to_response, mocked

        computed = suggest._build_items(query_params, elasticsearch_result, title_fields, class_fields)
        expected = {
            "@id": "http://semantica.globo.com/place/City/9d9e1ae6-a02f-4c2e-84d3-4219bf9d243a",
            "title": "Globoland",
            "rdfs:label": "Globoland",
            "@type": "http://semantica.globo.com/place/City",
            "type_title": "Cidade",
            "_type_title": "Cidade"
        }

        self.assertEqual(len(computed), 1)
        self.assertDictEqual(expected, computed[0])

    @patch("brainiak.suggest.suggest.get_subproperties", return_value=["property1", "property2"])
    def test_get_search_fields(self, mocked_get_subproperties):
        expected = {"property1", "property2", "rdfs:label"}
        search_params = {
            "search": {
                "fields": ["rdfs:label"]
            }
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

        response_set = suggest._get_response_fields_from_classes_dict(fields_by_class_list, response_fields, classes)
        self.assertEqual(expected_set, response_set)

    def test_get_response_fields_from_classes_dict_empty(self):
        expected_set = set([])
        response_fields = set(["field1"])
        classes = ["type"]

        fields_by_class_list = []

        response_set = suggest._get_response_fields_from_classes_dict(fields_by_class_list,
                                                                             response_fields, classes)
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

    def test_convert_index_name_to_graph_uri(self):
        graph_name = "semantica.dbpedia"
        computed = suggest.convert_index_name_to_graph_uri(graph_name)
        expected = "http://dbpedia.org/ontology/"
        self.assertEqual(computed, expected)


SAMPLE_RESPOSE_TO_GET_PREDICATE_RANGES = {
    u'results': {
        u'bindings': [
            {
                u'range': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/State'
                },
                u'range_graph': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/'
                },
                u'range_label': {
                    u'type': u'literal',
                    u'value': u'Estado',
                    u'xml:lang': u'pt'
                }
            },
            {
                u'range': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/Country'
                },
                u'range_graph': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/'
                },
                u'range_label': {
                    u'type': u'literal',
                    u'value': u'Pa\xeds',
                    u'xml:lang': u'pt'
                }
            },
            {
                u'range': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/City'
                },
                u'range_graph': {
                    u'type': u'uri',
                    u'value': u'http://semantica.globo.com/place/'
                },
                u'range_label': {
                    u'type': u'literal',
                    u'value': u'Cidade',
                    u'xml:lang': u'pt'
                }
            },
        ]
    }
}

SAMPLE_ES_RESPONSE = {
    u'hits': {
        u'hits': [
            {
                u'_score': 0.09596372,
                u'_type': u'http://semantica.globo.com/place/City',
                u'_id': u'http://semantica.globo.com/place/City/bc9e708f-35c4-4067-836d-48aaa51d746d',
                u'fields': {
                    u'http://semantica.globo.com/upper/name': u'Globoland: is the best'
                },
                u'_index': u'semantica.place'
            },
        ],
        'total': 1
    }
}

SAMPLE_BUILD_ITEMS = [
    {
        'type_title': u'Cidade',
        '@id': u'http://semantica.globo.com/place/City/bc9e708f-35c4-4067-836d-48aaa51d746d',
        '@type': u'http://semantica.globo.com/place/City',
        'title': u'Globoland: is the best'
    }
]


class ExtraSuggestTestCase(TestCase):

    @patch("brainiak.suggest.suggest.resources.decorate_dict_with_pagination")
    @patch("brainiak.suggest.suggest._build_items", return_value=SAMPLE_BUILD_ITEMS)
    @patch("brainiak.suggest.suggest.run_search", return_value=SAMPLE_ES_RESPONSE)
    @patch("brainiak.suggest.suggest.run_analyze", return_value={u'tokens': [{u'token': u'globoland'}]})
    @patch("brainiak.suggest.suggest.get_subproperties", return_value=[u'http://semantica.globo.com/upper/name'])
    @patch("brainiak.suggest.suggest._get_predicate_ranges", return_value=SAMPLE_RESPOSE_TO_GET_PREDICATE_RANGES)
    def test_do_suggest_with_data(self, mock_get_predicate_ranges, mock_get_subproperties, mock_run_analyze, mock_run_search, mock_build_items, mock_decorate):
        handler = MockHandler()
        params = {
            'lang': 'pt',
            'expand_uri': '0',
            'do_item_count': '0',
            'per_page': '10',
            'page': '0'
        }
        query_params = ParamDict(handler, **params)
        suggest_params = {
            u'search': {
                u'target': u'http://semantica.globo.com/upper/isPartOf',
                u'pattern': u'Globoland',
                u'graphs': [u'http://semantica.globo.com/place/'],
                u'classes': [u'http://semantica.globo.com/place/City'],
                u'fields': [u'http://semantica.globo.com/upper/name', u'http://semantica.globo.com/upper/fullName']
            }
        }

        computed = suggest.do_suggest(query_params, suggest_params)
        expected = {
            '@context': {'@language': 'pt'},
            '_base_url': 'http://mock.test.com/',
            'items': [
                {
                    '@id': u'http://semantica.globo.com/place/City/bc9e708f-35c4-4067-836d-48aaa51d746d',
                    '@type': u'http://semantica.globo.com/place/City',
                    'title': u'Globoland: is the best',
                    'type_title': u'Cidade'
                }
            ]
        }
        self.assertEqual(computed, expected)

    @patch("brainiak.suggest.suggest.run_search", return_value={"hits": {"total": 0}})
    @patch("brainiak.suggest.suggest.run_analyze", return_value={u'tokens': []})
    @patch("brainiak.suggest.suggest.get_subproperties", return_value=[])
    @patch("brainiak.suggest.suggest._get_predicate_ranges", return_value=SAMPLE_RESPOSE_TO_GET_PREDICATE_RANGES)
    def test_do_suggest_without_data(self, mock_get_predicate_ranges, mock_get_subproperties, mock_run_analyze, mock_run_search):
        handler = MockHandler()
        params = {
            'lang': 'pt',
            'expand_uri': '0',
            'do_item_count': '0',
            'per_page': '10',
            'page': '0'
        }
        query_params = ParamDict(handler, **params)
        suggest_params = {
            u'search': {
                u'target': u'http://semantica.globo.com/upper/isPartOf',
                u'pattern': u'Globoland',
                u'graphs': [u'http://semantica.globo.com/place/'],
                u'classes': [u'http://semantica.globo.com/place/City'],
                u'fields': [u'http://semantica.globo.com/upper/name', u'http://semantica.globo.com/upper/fullName']
            }
        }

        computed = suggest.do_suggest(query_params, suggest_params)
        self.assertEqual(computed, {})

    @patch("brainiak.suggest.suggest._get_predicate_ranges", return_value={u'results': {u'bindings': []}})
    def test_do_suggest_without_predicate_definition(self, mock_get_predicate_ranges):
        query_params = {}
        suggest_params = {u'search': {"target": "something"}}
        with self.assertRaises(HTTPError) as exception:
            suggest.do_suggest(query_params, suggest_params)
            expected_error_msg = \
                u"Either the predicate something does not exists or it does not have any rdfs:range defined in the triplestore"
            self.assertEqual(exception.exception, expected_error_msg)
