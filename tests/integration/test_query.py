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


QUERY_ENTAILMENT = """
SELECT ?name
WHERE {?person <http://graph.sample/name> ?name}
"""


# For more information on query entailment:
# http://www.w3.org/TR/sparql11-overview/
# session "5 SPARQL 1.1 Entailment Regimes"

# class SubpropertyEntailmentQueryTestCase(QueryTestCase):
#     allow_triplestore_connection = True
#     fixtures = ["tests/sample/subproperty.n3"]

#     def test_subproperty_entailment_query(self):
#         response_bindings = self.query(QUERY_ENTAILMENT)["results"]["bindings"]
#         import pdb; pdb.set_trace()
