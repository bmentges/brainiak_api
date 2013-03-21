from brainiak.instance.delete_instance import query_delete, query_dependants
from brainiak import triplestore
from tests.sparql import QueryTestCase


EXPECTED_DEPENDANTS_JSON = {
    u'head': {u'link': [], u'vars': [u'dependant']},
    u'results': {u'bindings': [
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/Platypus'}},
        {u'dependant': {u'type': u'uri', u'value': 'http://tatipedia.org/Teinolophos'}}],
        u'distinct': False,
        u'ordered': True}
}

EXPECTED_DELETE_JSON = {
    u"head": {u"link": [], u"vars": [u"callret-0"]},
    u"results": {u"distinct": False, "ordered": True, "bindings": [
    {"callret-0": {"type": "literal", "value": "Delete from <http://graph.sample>, 4 (or less) triples -- done"}}
    ]}}


class DeleteQueriesTestCase(QueryTestCase):

    allow_triplestore_connection = True
    graph_uri = "http://graph.sample"
    fixtures = ["tests/sample/instances.n3"]

    def setUp(self):
        self.original_query_sparql = triplestore.query_sparql

    def tearDown(self):
        triplestore.query_sparql = self.original_query_sparql

    def test_dependants_query(self):
        triplestore.query_sparql = lambda query: self.query(query)
        response_bindings = query_dependants("http://tatipedia.org/Australia")
        expected_binding = EXPECTED_DEPENDANTS_JSON

        self.assertEqual(len(response_bindings), len(expected_binding))
        for item in expected_binding:
            self.assertIn(item, response_bindings)

    def test_delete_query(self):
        triplestore.query_sparql = lambda query: self.query(query)
        response = query_delete(self.graph_uri, "http://tatipedia.org/Platypus")
        expected = EXPECTED_DELETE_JSON

        self.assertEqual(len(response), len(expected))
        self.assertEqual(response, expected)
