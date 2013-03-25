import unittest
from tornado.web import HTTPError
from brainiak.instance import create_resource
from brainiak.instance.create_resource import create_explicit_triples, create_implicit_triples, join_prefixes, join_triples, unpack_tuples, is_response_successful, create_instance


class CreateTriplesTestCase(unittest.TestCase):

    def test_create_explicit_triples_all_predicates_and_objects_are_compressed_uris(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com"},
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:gender": "personpedia:Male",
            "personpedia:wife": "personpedia:ConstanceLloyd"
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:gender", "personpedia:Male"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:wife", "personpedia:ConstanceLloyd")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_and_objects_are_full_uris(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "http://personpedia.com/birthPlace": "http://placepedia.com/Dublin",
            "http://personpedia.com/gender": "http://personpedia.com/Male",
            "http://personpedia.com/wife": "http://personpedia.com/ConstanceLloyd"
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/birthPlace>", "<http://placepedia.com/Dublin>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/gender>", "<http://personpedia.com/Male>"),
            ("<http://personpedia.com/Person/OscarWilde>", "<http://personpedia.com/wife>", "<http://personpedia.com/ConstanceLloyd>")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_objects_are_literals(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "personpedia:birthDate": "16/10/1854",
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:occupation": "writer",
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthDate", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:occupation", '"writer"')
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_literal_and_is_translated(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {},
            "personpedia:birthDate": "16/10/1854",
            "personpedia:birthPlace": "place:Dublin",
            "personpedia:occupation": "'writer'@en",
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthDate", '"16/10/1854"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:birthPlace", "place:Dublin"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:occupation", "'writer'@en")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_create_explicit_triples_predicates_are_uris_and_one_object_is_list(self):
        instance_uri = "http://personpedia.com/Person/OscarWilde"
        instance_data = {
            "@context": {"personpedia": "http://personpedia.com"},
            "rdfs:label": "Oscar Wilde",
            "personpedia:gender": "personpedia:Male",
            "personpedia:child": ["personpedia:VyvyanHolland", "personpedia:CyrilHolland"]
        }
        response = create_explicit_triples(instance_uri, instance_data)
        expected = [
            ("<http://personpedia.com/Person/OscarWilde>", "rdfs:label", '"Oscar Wilde"'),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:gender", "personpedia:Male"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:child", "personpedia:VyvyanHolland"),
            ("<http://personpedia.com/Person/OscarWilde>", "personpedia:child", "personpedia:CyrilHolland")
        ]
        self.assertEqual(sorted(response), sorted(expected))

    def test_unpack_tuples(self):
        instance_data = {
            "key1": "1a",
            "key2": ["2a", "2b"]
        }
        computed = unpack_tuples(instance_data)
        expected = [("key1", "1a"), ("key2", "2a"), ("key2", "2b")]
        self.assertEqual(sorted(computed), sorted(expected))
        self.assertEqual(len(instance_data), 1)
        self.assertEqual(instance_data["key1"], "1a")

    def test_create_implicit_triples(self):
        instance_uri = "http://instance"
        class_uri = "http://class"
        computed = create_implicit_triples(instance_uri, class_uri)
        expected = [("<http://instance>", "a", "<http://class>")]
        self.assertEqual(computed, expected)

    def test_join_triples_empty(self):
        triples = []
        computed = join_triples(triples)
        expected = ''
        self.assertEqual(computed, expected)

    def test_join_triples(self):
        triples = [
            ("<a>", "<b>", "<c>"),
            ("<d>", "<e>", "<f>"),
            ("<g>", "<h>", "<i>")
        ]
        computed = join_triples(triples)
        expected = '   <a> <b> <c> .\n   <d> <e> <f> .\n   <g> <h> <i> .'
        self.assertEqual(computed, expected)

    def test_join_prefixes_empty(self):
        prefixes = {}
        computed = join_prefixes(prefixes)
        expected = ''
        self.assertEqual(computed, expected)

    def test_join_prefixes(self):
        prefixes = {"base": "http://base.com", "upper": "http://upper.com"}
        computed = join_prefixes(prefixes)
        expected = 'PREFIX upper: <http://upper.com>\nPREFIX base: <http://base.com>'
        self.assertEqual(computed, expected)


class MockedTestCase(unittest.TestCase):

    def setUp(self):
        self.original_query_create_instances = create_resource.query_create_instances
        self.original_create_explicit_triples = create_resource.create_explicit_triples
        self.original_create_implicit_triples = create_resource.create_implicit_triples

    def tearDown(self):
        create_resource.query_create_instances = self.original_query_create_instances
        create_resource.create_explicit_triples = self.original_create_explicit_triples
        create_resource.create_implicit_triples = self.original_create_implicit_triples

    def test_create_instance_raises_500(self):
        query_params = {"class_uri": "anything", "graph_uri": "anything"}
        create_resource.query_create_instances = lambda x, y, z: None
        create_resource.create_explicit_triples = lambda x, y: []
        create_resource.create_implicit_triples = lambda x, y: []
        self.assertRaises(HTTPError, create_instance, query_params, {})
