import unittest

from mock import patch

from brainiak.collection.get_collection import Query, merge_by_id, build_json,\
    cast_item, cast_items_values, build_map_property_to_type
from brainiak.utils.params import LIST_PARAMS, ParamDict
from tests.mocks import MockRequest, MockHandler
from tests.sparql import strip
from tests.utils import URLTestCase


class CastItemTestCase(unittest.TestCase):

    def test_cast_item(self):
        item = {
            "name": "Armando",
            "marriedTo": "Regina",
            "age": "82",
            "weight": "84.5",
            "canCode": "0"
        }
        property_to_type = {
            "name": str,
            "age": int,
            "weight": float,
            "canCode": bool
        }
        computed = cast_item(item, property_to_type)
        expected = {
            "name": "Armando",
            "marriedTo": "Regina",
            "age": 82,
            "weight": 84.5,
            "canCode": False
        }
        self.assertEqual(computed, expected)

    def test_cast_item_containing_list(self):
        item = {
            "team": "Semantic Team",
            "grade": ["10", "10", "10"]
        }
        property_to_type = {
            "team": str,
            "grade": float
        }
        computed = cast_item(item, property_to_type)
        expected = {
            "team": "Semantic Team",
            "grade": [10.0, 10.0, 10.0]
        }
        self.assertEqual(computed, expected)

    def test_cast_items_values(self):
        items_list = [
            {
                "name": "Strogonof",
                "calories": "600.0",
                "isVegetarian": "0"
            },
            {
                "name": "Pesto Gnocchi",
                "calories": "323.7",
                "isVegetarian": "1"
            }
        ]
        class_properties = {
            "name": {"datatype": "http://www.w3.org/2001/XMLSchema#string"},
            "calories": {"datatype": "http://www.w3.org/2001/XMLSchema#float"},
            "isVegetarian": {"datatype": "http://www.w3.org/2001/XMLSchema#boolean"}
        }
        computed = cast_items_values(items_list, class_properties)
        expected = [
            {
                "name": "Strogonof",
                "calories": 600.0,
                "isVegetarian": False
            },
            {
                "name": "Pesto Gnocchi",
                "calories": 323.7,
                "isVegetarian": True
            }
        ]


class BuildMapPropertyToTypeTestCase(object):

    def test_build_map_propert_to_type_xsddateTime(self):
        properties = {
            "releaseDate": {
                "datatype": "xsd:dateTime"
            }
        }
        computed = build_map_property_to_type(properties)
        expected = {}
        self.assertEqual(computed, expected)

    def test_build_map_propert_to_type_float_bool_string_int(self):
        properties = {
            "http://on.to/weight": {
                "datatype": "http://www.w3.org/2001/XMLSchema#float"
            },
            "http://on.to/isHuman": {
                "datatype": "http://www.w3.org/2001/XMLSchema#boolean"
            },
            "http://on.to/name": {
                "datatype": "http://www.w3.org/2001/XMLSchema#string"
            },
            "http://on.to/age": {
                "datatype": "http://www.w3.org/2001/XMLSchema#int"
            }
        }
        computed = build_map_property_to_type(properties)
        expected = {
            "http://on.to/weight": float,
            "http://on.to/isHuman": bool,
            "http://on.to/name": str,
            "http://on.to/age": int
        }
        self.assertEqual(computed, expected)

    def test_build_map_property_to_type_object_property(self):
        properties = {
            "livesIn": {
                "range": {
                    "something"
                }
            }
        }
        computed = build_map_property_to_type(properties)
        expected = {}
        self.assertEqual(computed, expected)


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

    @patch("brainiak.collection.get_collection.get_class.get_cached_schema", return_value={"properties": {}})
    def test_query_without_extras_other(self, mock_get_schema):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name="zoo",
                           class_name="Lion",
                           **(LIST_PARAMS))
        items = []

        something = build_json(items, params)
        self.assertEqual(something["@context"], {'@language': 'pt'})
        self.assertEqual(something["items"], [])

    @patch("brainiak.collection.get_collection.get_class.get_cached_schema", return_value={"properties": {}})
    def test_query_with_prev_and_next_args_with_sort_by(self, mock_get_schema):
        handler = MockHandler(querystring="page=2&per_page=1&sort_by=rdfs:label")
        params = ParamDict(handler, context_name="subject", class_name="Maths", **(LIST_PARAMS))
        items = []
        computed = build_json(items, params)
        self.assertQueryStringArgsEqual(computed["_previous_args"], 'per_page=1&page=1&sort_by=rdfs%3Alabel')
        self.assertQueryStringArgsEqual(computed["_next_args"], 'per_page=1&page=3&sort_by=rdfs%3Alabel')

    @patch("brainiak.collection.get_collection.get_class.get_cached_schema", return_value={"properties": {}})
    def test_query_with_prev_and_next_args_with_sort_by_and_lang(self, mock_get_schema):
        handler = MockHandler(querystring="page=2&per_page=1&sort_by=rdfs:label&lang=en")
        params = ParamDict(handler, context_name="subject", class_name="Maths", **(LIST_PARAMS))
        items = []
        computed = build_json(items, params)
        self.assertQueryStringArgsEqual(computed["_previous_args"], 'per_page=1&page=1&sort_by=rdfs%3Alabel&lang=en')
        self.assertQueryStringArgsEqual(computed["_next_args"], 'per_page=1&page=3&sort_by=rdfs%3Alabel&lang=en')

    @patch("brainiak.collection.get_collection.get_class.get_cached_schema", return_value={"properties": {}})
    def test_query_with_extras(self, mock_get_schema):
        handler = MockHandler(querystring="class_prefix=Xubiru")
        params = ParamDict(handler,
                           context_name="zoo",
                           class_name="Lion",
                           **(LIST_PARAMS))
        items = []
        something = build_json(items, params)
        self.assertEqual(something["@context"], {'@language': 'pt'})
        self.assertEqual(something["items"], [])
