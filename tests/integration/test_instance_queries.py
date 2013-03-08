from brainiak.instance.resource import QUERY_FILTER_INSTANCE
from tests.sparql import build_json, QueryTestCase


class InstancesQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    fixtures = ["tests/sample/instances.n3"]

    def test_instance_filter_query_by_predicate_and_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/likes>",
            "object": "<http://tatipedia.org/Capoeira>"
        }

        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_object(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "?predicate",
            "object": "<http://tatipedia.org/BungeeJump>"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_predicate(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/dislikes>",
            "object": "?object"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}}]
        expected = build_json(bindings)

        self.assertEquals(computed, expected)

    def test_instance_filter_query_by_predicate_with_multiple_response(self):
        params = {
            "class_uri": "http://tatipedia.org/Person",
            "predicate": "<http://tatipedia.org/likes>",
            "object": "?object"
        }
        query = QUERY_FILTER_INSTANCE % params
        computed = self.query(query)

        bindings = [{u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/mary'}},
                    {u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/john'}}]

        expected = build_json(bindings)

        self.assertEquals(computed, expected)
