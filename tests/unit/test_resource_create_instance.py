import unittest
from brainiak.instance.create_resource import create_explicit_triples


class CreateInstanceTestCase(unittest.TestCase):

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
