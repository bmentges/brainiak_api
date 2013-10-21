import unittest
from tornado.web import HTTPError
from brainiak.instance import common


class TestCaseInstanceResource(unittest.TestCase):

    def test_must_retrieve_graph_and_class_uri_is_true(self):
        query_params = {
            "class_name": u"_",
            "graph_uri": u"_",
            "instance_id": u"_",
            "instance_uri": u"instance_uri"
        }
        response = common.must_retrieve_graph_and_class_uri(query_params)
        self.assertTrue(response)

    def test_must_retrieve_graph_and_class_uri_is_false_due_to_graph_uri(self):
        query_params = {
            "class_name": u"_",
            "graph_uri": u"some_uri",
            "instance_id": u"_",
            "instance_uri": u"some_uri",
        }
        response = common.must_retrieve_graph_and_class_uri(query_params)
        self.assertFalse(response)

    def test_must_retrieve_graph_and_class_uri_is_false_due_to_class_name(self):
        query_params = {
            "class_name": u"some_class",
            "graph_uri": u"_",
            "instance_id": u"_",
            "instance_uri": u"some_uri",
        }
        response = common.must_retrieve_graph_and_class_uri(query_params)
        self.assertFalse(response)

    def test_must_retrieve_graph_and_class_uri_raises_exception(self):
        query_params = {}
        with self.assertRaises(HTTPError) as exception:
            common.must_retrieve_graph_and_class_uri(query_params)
        msg = "HTTP 404: Not Found (Parameter <'class_name'> is missing in order to update instance.)"
        self.assertEqual(str(exception.exception), msg)


    def test_extract_class_uri(self):
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            },
            {

                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            }
        ]
        response = common.extract_class_uri(bindings)
        expected = u'http://dbpedia.org/ontology/News'
        self.assertEqual(response, expected)
        self.assertFalse('class_uri' in bindings[0])
        self.assertFalse('class_uri' in bindings[1])

    def test_extract_graph_uri(self):
        bindings = [
            {
                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'},
                u'object': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'object_label': {u'type': u'literal', u'value': u'News'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            },
            {

                u'predicate': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#label'},
                u'object': {u'type': u'literal', u'value': u'Cricket becomes the most popular sport of Brazil'},
                u'class_uri': {u'type': u'uri', u'value': u'http://dbpedia.org/ontology/News'},
                u'graph_uri': {u'type': u'uri', u'value': u'http://brmedia.com/'}
            }
        ]
        response = common.extract_graph_uri(bindings)
        expected = u'http://brmedia.com/'
        self.assertEqual(response, expected)
        self.assertFalse('graph_uri' in bindings[0])
        self.assertFalse('graph_uri' in bindings[1])

