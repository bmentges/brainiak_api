import unittest

from brainiak.instance.list_resource import Query


def strip(query_string):
    return [item.strip() for item in query_string.split("\n") if item.strip() != '']


class ListQueryTestCase(unittest.TestCase):

    default_params = {
            "class_uri": "http://some.graph/SomeClass",
            "lang": "",
            "graph_uri": "http://some.graph/",
            "per_page": "10",
            "page": "0",
            "p": "?predicate",
            "o": "?object",
            "sort_by": "",
            "sort_order": "asc"
    }
    maxDiff = None

    def test_query_without_extras(self):
        params = self.default_params
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_pagination(self):
        params = self.default_params.copy()
        params["per_page"] = "15"
        params["page"] = "2"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label .
        }
        LIMIT 15
        OFFSET 30
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_predicate_as_uri(self):
        params = self.default_params.copy()
        params["p"] = "http://some.graph/predicate"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://some.graph/predicate> ?object .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_predicate_as_rdfs_label(self):
        params = self.default_params.copy()
        params["p"] = "rdfs:label"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_predicate_as_compressed_uri(self):
        params = self.default_params.copy()
        params["p"] = "schema:Creature"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://schema.org/Creature> ?object .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_predicate_and_object_as_literal(self):
        params = self.default_params.copy()
        params["p"] = "schema:Creature"
        params["o"] = "Xubiru"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://schema.org/Creature> "Xubiru" .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_predicate_and_object_as_literal_with_lang(self):
        params = self.default_params.copy()
        params["p"] = "schema:Creature"
        params["o"] = "Xubiru"
        params["lang"] = "pt"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://schema.org/Creature> "Xubiru"@pt .
            FILTER(langMatches(lang(?label), "pt") OR langMatches(lang(?label), "")) .
        }
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_sort_by(self):
        params = self.default_params.copy()
        params["sort_by"] = "dbpedia:predicate"
        params["sort_order"] = "asc"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?sort_object, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://dbpedia.org/ontology/predicate> ?sort_object .
        }
        ORDER BY ASC(?sort_object)
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_desc_sort_by_rdfs_label(self):
        params = self.default_params.copy()
        params["sort_by"] = "rdfs:label"
        params["sort_order"] = "desc"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label .
        }
        ORDER BY DESC(?label)
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_sort_by_object_of_predicate(self):
        params = self.default_params.copy()
        params["p"] = "schema:another_predicate"
        params["sort_by"] = "schema:another_predicate"
        params["sort_order"] = "desc"
        query = Query(params)
        computed = query.to_string()
        expected = """
        DEFINE input:inference <http://semantica.globo.com/ruleset>
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            ?subject a <http://some.graph/SomeClass> ;
                     rdfs:label ?label ;
                     <http://schema.org/another_predicate> ?object .
        }
        ORDER BY DESC(?object)
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))
