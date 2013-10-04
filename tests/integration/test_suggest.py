# -*- coding: utf-8 -*-
import json
from urllib import quote_plus

import requests

from mock import patch

from brainiak.suggest.suggest import QUERY_PREDICATE_RANGES, \
    QUERY_SUBPROPERTIES, _build_class_fields_query, _build_predicate_values_query
from brainiak.utils.sparql import filter_values, compress_keys_and_values
from brainiak import settings

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase


class TestRangeSearch(TornadoAsyncHTTPTestCase, QueryTestCase):

    allow_triplestore_connection = True
    fixtures = ["tests/sample/animalia.n3"]
    graph_uri = "http://example.onto/"

    maxDiff = None

    VALID_BODY_PARAMS = {
        'search': {
            'pattern': 'york',
            'target': 'http://example.onto/birthPlace'
        }
    }

    def setUp(self):
        super(TestRangeSearch, self).setUp()
        # ONLY VALID FOR VALID_BODY_PARAMS
        self.elastic_request_url = "http://" + settings.ELASTICSEARCH_ENDPOINT + "/semantica.example.onto/"
        self.elastic_request_url += quote_plus("http://example.onto/City") + "/"
        self.elastic_request_url += quote_plus("http://example.onto/York")
        entry = {
            "http://www.w3.org/2000/01/rdf-schema#label": "York",
            "http://example.onto/nickname": "City of York",
            "http://example.onto/description": "York is a walled city, situated at the confluence of the Rivers Ouse and Foss in North Yorkshire, England."
        }

        requests.put(self.elastic_request_url + "?refresh=true", data=json.dumps(entry))

    def tearDown(self):
        super(TestRangeSearch, self).setUp()
        requests.delete(self.elastic_request_url)

    def test_request_with_invalid_predicate(self):
        INVALID_PARAMS = {
            "search": {
                'pattern': 'york',
                'target': 'http://example.onto/invalidPredicate'
            }
        }
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(INVALID_PARAMS))
        self.assertEqual(response.code, 400)
        expected_error_msg = "HTTP error: 400\nEither the predicate http://example.onto/invalidPredicate does not exists or it does not have any rdfs:range defined in the triplestore"
        json_received = json.loads(response.body)
        self.assertIn(expected_error_msg, json_received['errors'])

    @patch("brainiak.suggest.suggest.uri_to_slug", return_value="example.onto")
    def test_successful_request(self, mocked_uri_to_slug):
        expected_items = [
            {
                u'@id': u'http://example.onto/York', u'title': u'York',
                u'@type': u'http://example.onto/City', u'type_title': u'City'
            }
        ]
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(self.VALID_BODY_PARAMS))
        self.assertEqual(response.code, 200)
        response_json = json.loads(response.body)
        self.assertEqual(expected_items, response_json["items"])

    @patch("brainiak.suggest.suggest.uri_to_slug", return_value="example.onto")
    def test_successful_request_with_metafields(self, mocked_uri_to_slug):
        expected_items = [
            {
                u'@id': u'http://example.onto/York', u'title': u'York',
                u'@type': u'http://example.onto/City', u'type_title': u'City',
                u"instance_fields": [
                    {
                        u"predicate_id": u"http://example.onto/description",
                        u"predicate_title": u"Description of a place",
                        u"object_title": u"York is a walled city, situated at the confluence of the Rivers Ouse and Foss in North Yorkshire, England.",
                        u"required": False
                    },
                    {
                        u"predicate_id": u"http://example.onto/nickname",
                        u"predicate_title": u"Nickname of a place",
                        u"object_title": u"City of York",
                        u"required": False
                    }
                ]
            }
        ]

        VALID_BODY_PARAMS_WITH_METAFIELDS = dict(self.VALID_BODY_PARAMS)
        VALID_BODY_PARAMS_WITH_METAFIELDS.update({
            "response": {
                "meta_fields": ["http://example.onto/suggestMetaField"]
            }
        })
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(VALID_BODY_PARAMS_WITH_METAFIELDS))
        self.assertEqual(response.code, 200)
        response_json = json.loads(response.body)
        self.assertEqual(expected_items, response_json["items"])

    @patch("brainiak.suggest.suggest.uri_to_slug", return_value="example.onto")
    def test_zero_results(self, mocked_uri_to_slug):
        zero_results_parameters = {
            "search": {
                "pattern": "non existent keywords",
                "target": "http://example.onto/birthPlace"
            }
        }
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(zero_results_parameters))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, '{}')

    def test_suggest_without_required_param_target(self):
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps({'search': {'pattern': 1}}))
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertIn("'target' is a required property", json_received['errors'][0])

    def test_suggest_with_invalid_body_param(self):
        d = {'invalid': 3}
        d.update(self.VALID_BODY_PARAMS)
        response = self.fetch('/_suggest',
                              method='POST',
                              body=json.dumps(d))
        self.assertEqual(response.code, 400)
        json_received = json.loads(response.body)
        self.assertIn("Additional properties are not allowed (u'invalid' was unexpected)", json_received['errors'][0])

    def test_query_predicate_superclass_range(self):
        expected_classes = ["http://example.onto/Place", "http://example.onto/City"]
        expected_labels = ["Place", "City"]
        expected_graphs = ["http://example.onto/", "http://example.onto/"]

        query_params = {
            "target": "http://example.onto/birthPlace",
            "lang_filter_range_label": ""
        }
        query_response = self.query(QUERY_PREDICATE_RANGES % query_params)
        response_classes = filter_values(query_response, "range")
        response_labels = filter_values(query_response, "range_label")
        response_graphs = filter_values(query_response, "range_graph")

        self.assertEqual(expected_classes, response_classes)
        self.assertEqual(expected_labels, response_labels)
        self.assertEqual(expected_graphs, response_graphs)

    def test_query_subproperties(self):
        expected = ["http://example.onto/birthCity"]
        query_response = self.query(QUERY_SUBPROPERTIES % "http://example.onto/birthPlace")
        response = filter_values(query_response, "property")
        self.assertEqual(expected, response)

    def test_query_meta_fields(self):
        expected = ["http://example.onto/nickname, http://example.onto/description"]
        classes = ["http://example.onto/City"]
        meta_field = "http://example.onto/suggestMetaField"
        query = _build_class_fields_query(classes, meta_field)
        query_response = self.query(query)
        meta_field_values = filter_values(query_response, "field_value")
        self.assertEqual(expected, meta_field_values)

    def test_query_predicate_values(self):
        expected = [
            {
                u'predicate': u'http://example.onto/nickname',
                u'predicate_title': u'Nickname of a place',
                u'object_value': u'City of York'
            },
            {
                u'predicate': u'http://example.onto/description',
                u'predicate_title': u'Description of a place',
                u'object_value': u'York is a walled city, situated at the confluence of the Rivers Ouse and Foss in North Yorkshire, England.'
            }
        ]
        instance_uri = "http://example.onto/York"
        instance_fields = ["http://example.onto/nickname", "http://example.onto/description"]
        query = _build_predicate_values_query(instance_uri, instance_fields)
        query_response = self.query(query)
        values = compress_keys_and_values(query_response)
        self.assertEqual(expected, values)
