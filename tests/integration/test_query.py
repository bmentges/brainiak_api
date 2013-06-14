from tests.sparql import QueryTestCase


EXPECTED_JSON = {
    u'head': {u'link': [], u'vars': [u's', u'p', u'o']},
    u'results': {u'bindings': [
        {u'o': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                u'type': u'typed-literal',
                u'value': u'26'},
         u'p': {u'type': u'uri', u'value': u'#age'},
         u's': {u'type': u'uri', u'value': u'#icaro'}},
        {u'o': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                u'type': u'typed-literal',
                u'value': u'38'},
         u'p': {u'type': u'uri', u'value': u'#age'},
         u's': {u'type': u'uri', u'value': u'#senra'}},
        {u'o': {u'datatype': u'http://www.w3.org/2001/XMLSchema#integer',
                u'type': u'typed-literal',
                u'value': u'28'},
         u'p': {u'type': u'uri', u'value': u'#age'},
         u's': {u'type': u'uri', u'value': u'#tati'}}],
        u'distinct': False,
        u'ordered': True}
}


DUMMY_QUERY = "SELECT * WHERE {?s ?p ?o}"


class DummyQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    #graph_uri = "http://graph.sample"
    fixtures = ["tests/sample/demo.n3"]

    def test_dummy_query(self):
        response_bindings = self.query(DUMMY_QUERY)["results"]["bindings"]
        expected_binding = EXPECTED_JSON["results"]["bindings"]
        self.assertEqual(len(response_bindings), len(expected_binding))
        for item in expected_binding:
            self.assertIn(item, response_bindings)


QUERY_PROPERTY_ENTAILMENT = """
DEFINE input:inference <http://tatipedia.org/ruleset>
SELECT DISTINCT ?subject ?label
WHERE {
    ?subject a <http://tatipedia.org/Place>;
             rdfs:label ?label  .
    FILTER (langMatches(lang(?label), "pt"))
}
"""


class SubpropertyEntailmentQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    graph_uri = "http://tatipedia.org/"
    fixtures = ["tests/sample/subproperty.n3"]

    def test_subproperty_entailment_query(self):
        response_bindings = self.query(QUERY_PROPERTY_ENTAILMENT)["results"]["bindings"]
        expected_bindings = [
            {u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Nova Iorque'},
             u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/new_york'}},
            {u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Londres'},
             u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/london'}},
            {u'label': {u'xml:lang': u'pt', u'type': u'literal', u'value': u'Munique'},
             u'subject': {u'type': u'uri', u'value': u'http://tatipedia.org/munich'}}
        ]
        self.assertEqual(sorted(response_bindings), sorted(expected_bindings))


QUERY_LIST_GRAPHS = """
SELECT DISTINCT ?graph
WHERE {
    GRAPH ?graph {?s a ?o}
}
"""


class GraphQueryTestCase(QueryTestCase):
    allow_triplestore_connection = True
    graph_uri = "http://xubirupedia.org/"
    fixtures = ["tests/sample/subproperty.n3"]

    def test_list_graphs(self):
        response_bindings = self.query(QUERY_LIST_GRAPHS)["results"]["bindings"]
        expected_item = {
            u'graph': {u'type': u'uri', u'value': u'http://xubirupedia.org/'}
        }
        self.assertIn(expected_item, response_bindings)
