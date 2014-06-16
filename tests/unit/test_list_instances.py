import unittest

from brainiak.collection.get_collection import Query, merge_by_id, build_json,\
    sort_values_of_properties_which_map_lists
from brainiak.utils.params import LIST_PARAMS, ParamDict
from tests.mocks import MockRequest, MockHandler
from tests.sparql import strip
from tests.utils import URLTestCase


class SortItemsListValuesTestCase(unittest.TestCase):

    def test_empty_list(self):
        sample_list = []
        computed = sort_values_of_properties_which_map_lists(sample_list)
        expected = []
        self.assertEqual(computed, expected)

    def test_list_of_items_without_list_values(self):
        sample_list = [
            {"c": "d"},
            {"a": "b"}
        ]
        computed = sort_values_of_properties_which_map_lists(sample_list)
        expected = [
            {"c": "d"},
            {"a": "b"}
        ]
        self.assertEqual(computed, expected)

    def test_list_of_items_with_list_values(self):
        sample_list = [
            {"prime": [17, 1, 3, 2, 5, 13, 11, 7]},
            {"fibo": [2, 34, 13, 1, 3, 21, 5, 1, 8]}
        ]
        computed = sort_values_of_properties_which_map_lists(sample_list)
        expected = [
            {"prime": [1, 2, 3, 5, 7, 11, 13, 17]},
            {"fibo": [1, 1, 2, 3, 5, 8, 13, 21, 34]}
        ]

class MergeByIdTestCase(unittest.TestCase):

    def test_no_merge(self):
        values = [
            {
                "@id": 1,
                "some property": "some value",
            },
            {
                "@id": 2,
                "some property": "some other value",
            }
        ]
        computed = merge_by_id(values)
        self.assertEqual(computed, values)

    def test_single_merge(self):
        values = [
            {
                "@id": 1,
                "some property": "some value",
            },
            {
                "@id": 2,
                "some property": "some other value",
            },
            {
                "@id": 1,
                "some property": "a thid value",
            }
        ]
        expected = [
            {
                "@id": 1,
                "some property": ["some value", "a thid value"],
            },
            {
                "@id": 2,
                "some property": "some other value",
            }
        ]
        computed = merge_by_id(values)
        self.assertEqual(computed, expected)

    def test_two_merges(self):
        values = [
            {
                "@id": 1,
                "some property": "some value",
            },
            {
                "@id": 2,
                "some property": "some other value",
            },
            {
                "@id": 1,
                "some property": "a thid value",
            },
            {
                "@id": 2,
                "some property": "last value",
            }
        ]
        expected = [
            {
                "@id": 1,
                "some property": ["some value", "a thid value"]
            },
            {
                "@id": 2,
                "some property": ["some other value", "last value"]
            }
        ]
        computed = merge_by_id(values)
        self.assertEqual(computed, expected)


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
            "sort_order": "asc",
            "sort_include_empty": "1"
    }
    maxDiff = None

    def test_query_without_extras(self):
        params = self.default_params
        query = Query(params)
        computed = query.to_string()
        expected = """
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
        }

        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_p1_and_o1(self):
        params = self.default_params.copy()
        params["p1"] = "some:predicate"
        params["o1"] = "some:object"
        query = Query(params)
        computed = query.to_string()
        expected = """
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     some:predicate some:object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
        }

        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_p1_o1_p2_o2(self):
        params = self.default_params.copy()
        params["p1"] = "some:predicate"
        params["o1"] = "some:object"
        params["p2"] = "another:predicate"
        params["o2"] = "?another_object"
        query = Query(params)
        computed = query.to_string()
        expected = """
        SELECT DISTINCT ?another_object, ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     another:predicate ?another_object OPTION(inference "http://semantica.globo.com/ruleset") ;
                     some:predicate some:object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
        }

        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_p3_o3(self):
        params = self.default_params.copy()
        params["p3"] = "?any_predicate"
        params["o3"] = "?any_object"
        query = Query(params)
        computed = query.to_string()
        expected = """
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://some.graph/predicate> ?object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://schema.org/Creature> ?object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://schema.org/Creature> ?literal1 OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
            FILTER(str(?literal1) = "Xubiru") .
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
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://schema.org/Creature> ?literal1 OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
            FILTER(str(?literal1) = "Xubiru") .
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
        SELECT DISTINCT ?label, ?sort_object, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
            OPTIONAL {?subject <http://dbpedia.org/ontology/predicate> ?sort_object} }
        }
        ORDER BY ASC(?sort_object)
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_query_with_sort_exclude_empty(self):
        params = self.default_params.copy()
        params["sort_by"] = "dbpedia:predicate"
        params["sort_order"] = "asc"
        params["sort_include_empty"] = "0"
        query = Query(params)
        computed = query.to_string()
        expected = """
        SELECT DISTINCT ?label, ?sort_object, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://dbpedia.org/ontology/predicate> ?sort_object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
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
        SELECT DISTINCT ?label, ?object, ?subject
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://schema.org/another_predicate> ?object OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
        }
        ORDER BY DESC(?object)
        LIMIT 10
        OFFSET 0
        """
        self.assertEqual(strip(computed), strip(expected))

    def test_count_query_without_extras(self):
        params = self.default_params
        query = Query(params)
        computed = query.to_string(count=True)
        expected = """
        SELECT count(DISTINCT ?subject) as ?total
        WHERE {
            GRAPH <http://some.graph/> { ?subject a <http://some.graph/SomeClass> OPTION(inference "http://semantica.globo.com/ruleset") ;
                     <http://www.w3.org/2000/01/rdf-schema#label> ?label OPTION(inference "http://semantica.globo.com/ruleset") .
                     }
        }
        """
        self.assertEqual(strip(computed), strip(expected))


class BuildJSONTestCase(URLTestCase):

    default_params = {
            "class_uri": "http://some.graph/SomeClass",
            "lang": "",
            "graph_uri": "http://some.graph/",
            "per_page": "10",
            "page": "0",
            "p": "?predicate",
            "o": "?object",
            "sort_by": "",
            "sort_order": "asc",
            "sort_include_empty": "1",
            "base_url": "http://domain.com",
            "request": MockRequest(),
    }
    maxDiff = None

    def test_query_without_extras_other(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name="zoo",
                           class_name="Lion",
                           **(LIST_PARAMS))
        items = []

        something = build_json(items, params)
        self.assertEqual(something["@context"], {'@language': 'pt'})
        self.assertEqual(something["items"], [])

        # TODO - migrar para um novo teste
        # links = something["links"]
        # expected_links = [
        #     {'href': 'http://mock.test.com/', 'method': 'GET', 'rel': 'self'},
        #     {
        #         'href': 'http://mock.test.com?per_page=10&page=1',
        #         'method': 'GET',
        #         'rel': 'first'
        #     },
        #     {
        #         'href': 'http://mock.test.com?per_page=10&page=2',
        #         'method': 'GET',
        #         'rel': 'next'
        #     },
        #     {
        #         'href': 'http://mock.test.com/{resource_id}?instance_prefix={instance_prefix}',
        #         'method': 'GET',
        #         'rel': 'item'
        #     },
        #     {
        #         'href': 'http://mock.test.com/{resource_id}?instance_prefix={instance_prefix}',
        #         'method': 'GET',
        #         'rel': 'instance'
        #     },
        #     {
        #         'href': 'http://mock.test.com/zoo/Lion/_schema',
        #         'method': 'GET',
        #         'rel': 'class'
        #     },
        #     {
        #         'href': 'http://mock.test.com/zoo/Lion',
        #         'method': 'POST',
        #         'rel': 'add',
        #         'schema': {'$ref': 'http://mock.test.com/zoo/Lion/_schema'}
        #     }
        # ]
        # self.assertEquals(sorted(links), sorted(expected_links))

    def test_query_with_prev_and_next_args_with_sort_by(self):
        handler = MockHandler(querystring="page=2&per_page=1&sort_by=rdfs:label")
        params = ParamDict(handler, context_name="subject", class_name="Maths", **(LIST_PARAMS))
        items = []
        computed = build_json(items, params)
        self.assertQueryStringArgsEqual(computed["_previous_args"], 'per_page=1&page=1&sort_by=rdfs%3Alabel')
        self.assertQueryStringArgsEqual(computed["_next_args"], 'per_page=1&page=3&sort_by=rdfs%3Alabel')

    def test_query_with_prev_and_next_args_with_sort_by_and_lang(self):
        handler = MockHandler(querystring="page=2&per_page=1&sort_by=rdfs:label&lang=en")
        params = ParamDict(handler, context_name="subject", class_name="Maths", **(LIST_PARAMS))
        items = []
        computed = build_json(items, params)
        self.assertQueryStringArgsEqual(computed["_previous_args"], 'per_page=1&page=1&sort_by=rdfs%3Alabel&lang=en')
        self.assertQueryStringArgsEqual(computed["_next_args"], 'per_page=1&page=3&sort_by=rdfs%3Alabel&lang=en')

    def test_query_with_extras(self):
        handler = MockHandler(querystring="class_prefix=Xubiru")
        params = ParamDict(handler,
                           context_name="zoo",
                           class_name="Lion",
                           **(LIST_PARAMS))
        items = []
        something = build_json(items, params)
        self.assertEqual(something["@context"], {'@language': 'pt'})
        self.assertEqual(something["items"], [])

        # TODO - migrar para um novo teste
        # links = something["links"]
        # expected_links = [
        #     {'href': 'http://mock.test.com/?class_prefix=Xubiru', 'method': 'GET', 'rel': 'self'},
        #     {'href': 'http://mock.test.com?per_page=10&page=1&class_prefix=Xubiru', 'method': 'GET', 'rel': 'first'},
        #     {'href': 'http://mock.test.com?per_page=10&page=2&class_prefix=Xubiru', 'method': 'GET', 'rel': 'next'},
        #     {'href': 'http://mock.test.com/zoo/Lion/_schema?class_prefix=Xubiru', 'method': 'GET', 'rel': 'class'},
        #     {'href': 'http://mock.test.com/{resource_id}?class_prefix=Xubiru&instance_prefix={instance_prefix}',
        #      'method': 'GET', 'rel': 'item'},
        #     {'href': 'http://mock.test.com/{resource_id}?class_prefix=Xubiru&instance_prefix={instance_prefix}',
        #      'method': 'GET', 'rel': 'instance'},
        #     {'href': 'http://mock.test.com/zoo/Lion?class_prefix=Xubiru', 'method': 'POST', 'rel': 'add',
        #      'schema': {'$ref': 'http://mock.test.com/zoo/Lion/_schema?class_prefix=Xubiru'}}
        # ]
        # self.assertEquals(sorted(links), sorted(expected_links))
