from tests.sparql import QueryTestCase
from brainiak.instance import common


class InstanceCommonTestCase(QueryTestCase):

    maxDiff = None
    fixtures_by_graph = {
        'http://any.graph/': ['tests/sample/instances.n3'],
        'http://empty.graph/': [],
        'http://test.edit.instance/': []
    }

    def test_query_get_class_and_graph(self):
        params = {
            "instance_uri": "http://tatipedia.org/Platypus"
        }
        query = common.QUERY_GET_CLASS_AND_GRAPH % params
        computed = self.query(query, False)['results']['bindings'][0]
        expected = {
            u'graph_uri': {u'type': u'uri', u'value': u'http://any.graph/'},
            u'class_uri': {u'type': u'uri', u'value': u'http://tatipedia.org/Species'}
        }
        self.assertEqual(computed, expected)
