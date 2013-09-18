# -*- coding: utf-8 -*-

import unittest
from jsonschema import validate, ValidationError

from brainiak.suggest.suggest import SUGGEST_PARAM_SCHEMA


class TestSuggestParams(unittest.TestCase):

    maxDiff = None

    def test_invalid_with_trash(self):
        invalid_case = {"search": {"pattern": "", "target": ""}, "trash": "This is unknown"}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_with_nested_trash(self):
        invalid_case = {"search": {"pattern": "", "target": "", "trash": "This is unknown"}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_without_target(self):
        invalid_case = {"search": {"pattern": "Bla"}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_graphs_type(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "graphs": "this should be an array"}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_fields_type(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "fields": "this should be an array"}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_graphs_empty(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "graphs": []}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_fields_empty(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "fields": []}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_graphs_duplicate(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "graphs": ["a", "a"]}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_search_fields_duplicate(self):
        invalid_case = {"search": {"target": "some_target_url", "pattern": "Bla", "fields": ["a", "a"]}}
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_valid_simple_case(self):
        valid_simple_case = {
            "search": {
                    "pattern": "Ronaldo",
                    "target": "http://semantica.globo.com/esportes/tem_como_conteudo",
            }
        }
        validate(valid_simple_case, SUGGEST_PARAM_SCHEMA)

    def test_valid_with_graph(self):
        valid_simple_case = {
            "search": {
                    "pattern": "Ronaldo",
                    "target": "http://semantica.globo.com/esportes/tem_como_conteudo",
                    "graphs": ["http://semantica.globo.com/esportes/"],
            }
        }
        validate(valid_simple_case, SUGGEST_PARAM_SCHEMA)

    def test_valid_with_graph(self):
        valid_simple_case = {
            "search": {
                    "pattern": "Ronaldo",
                    "target": "http://semantica.globo.com/esportes/tem_como_conteudo",
                    "graphs": ["http://semantica.globo.com/esportes/"],
            },
            "response": {
                "fields": ["esportes:nome_popular_sde", "esportes:composite"]
            }
        }
        validate(valid_simple_case, SUGGEST_PARAM_SCHEMA)
