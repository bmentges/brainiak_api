# -*- coding: utf-8 -*-

from unittest import TestCase
from jsonschema import validate, ValidationError

from brainiak.suggest.suggest import SUGGEST_PARAM_SCHEMA
from brainiak.suggest import json_schema as suggest_json_schema


class TestSuggestParams(TestCase):

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

    def test_invalid_response_fields_with_additional_param(self):
        invalid_case = {
            "search": {"target": "url", "pattern": "bla"},
            "response": {
                "invalid_param": "param"
            }
        }
        self.assertRaises(ValidationError, validate, invalid_case, SUGGEST_PARAM_SCHEMA)

    def test_invalid_response_fields_with_duplicated_classes_items(self):
        invalid_case = {
            "search": {"target": "url", "pattern": "bla"},
            "response": {
                "classes": [
                    {"@type": "type", "instance_fields": ["field"]},
                    {"@type": "type", "instance_fields": ["field"]}
                ]
            }
        }
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

    def test_valid_with_graphs_and_response(self):
        valid_simple_case = {
            "search": {
                "pattern": "Ronaldo",
                "target": "http://semantica.globo.com/esportes/tem_como_conteudo",
                "graphs": ["http://semantica.globo.com/esportes/"],
            },
            "response": {
                "instance_fields": ["esportes:nome_popular_sde", "esportes:composite"]
            }
        }
        validate(valid_simple_case, SUGGEST_PARAM_SCHEMA)

    def test_valid_with_details_response(self):
        valid_case = {
            "search": {
                "pattern": "Ronaldo",
                "target": "http://semantica.globo.com/esportes/tem_como_conteudo",
            },
            "response": {
                "meta_fields": ["base:detalhes_da_cortina"],
                "classes": [
                    {
                        "@type": "esportes:Atleta",
                        "instance_fields": ["esportes:nome_popular_sde", "esportes:composite"]
                    }
                ]
            }
        }
        validate(valid_case, SUGGEST_PARAM_SCHEMA)


class TestSuggestResponseJson(TestCase):

    def setUp(self):
        self.suggest_json_schema = suggest_json_schema.schema()

    def test_valid_json(self):
        valid_suggest_response = {
            "items": [
                {
                    "@id": "http://semantica.globo.com/esportes/Atleta/Ronaldo",
                    "title": "Ronaldinho o Fenômeno",
                    "@type": "http://semantica.globo.com/esportes/Atleta",
                    "type_title": "Atleta",
                    "class_fields": {
                        "base:thumbnail": "http://s-ct.glbimg.globoi.com/jo/eg/static/semantica/img/icones/ico_criatura.png",
                    },
                    "instance_fields": [
                        {
                            "predicate_id": "rdfs:label",
                            "predicate_title": "Nome",
                            "object_id": "http://semantica.globo.com/esportes/Atleta/Ronaldo",
                            "object_title": "Ronaldo O Fenômeno",
                            "required": True,
                        },
                        {
                            "predicate_id": "esportes:esta_no_time",
                            "predicate_title": "Pertence ao Time",
                            "object_id": "http://semantica.globo.com/esportes/Equipe/Botafogo",
                            "object_title": "Botafogo",
                            "required": False
                        },
                        {
                            "predicate_id": "esportes:posicao",
                            "predicate_title": "Posição",
                            "object_title": "VOL",
                            "required": False,
                        }
                    ]
                }
            ],
            "item_count": 1,
            "@context": {"esportes": "http://semantica.globo.com/esportes/"}
        }
        validate(valid_suggest_response, self.suggest_json_schema)

    def test_valid_minimal_json(self):
        minimal_valid_json = {
            "items": [
                {
                    "@id": "http://semantica.globo.com/esportes/Atleta/Ronaldo",
                    "title": "Ronaldinho o Fenômeno",
                    "@type": "http://semantica.globo.com/esportes/Atleta",
                    "type_title": "Atleta"
                }
            ]
        }

        validate(minimal_valid_json, self.suggest_json_schema)

    def test_invalid_json_with_additional_property_in_instance_fields(self):
        invalid_json_with_additional_property = {
            "items": [
                {
                    "@id": "http://semantica.globo.com/esportes/Atleta/Ronaldo",
                    "title": "Ronaldinho o Fenômeno",
                    "@type": "http://semantica.globo.com/esportes/Atleta",
                    "type_title": "Atleta",
                    "instance_fields": [
                        {
                            "invalid_param": "invalid_param_value",
                            "predicate_id": "rdfs:label",
                            "predicate_title": "Nome",
                            "object_id": "http://semantica.globo.com/esportes/Atleta/Ronaldo",
                            "object_title": "Ronaldo O Fenômeno",
                            "required": True,
                        }
                    ]
                }
            ]
        }

        try:
            validate(invalid_json_with_additional_property, self.suggest_json_schema)
        except ValidationError as e:
            self.assertIn("Additional properties are not allowed ('invalid_param' was unexpected)",
                          str(e))
        else:
            self.fail("A ValidationError should be raised")

    def test_invalid_json_with_missing_id_in_item(self):
        invalid_json_with_missing_id = {
            "items": [
                {
                    "title": "Ronaldinho o Fenômeno",
                    "@type": "http://semantica.globo.com/esportes/Atleta",
                    "type_title": "Atleta",
                }
            ]
        }

        try:
            validate(invalid_json_with_missing_id, self.suggest_json_schema)
        except ValidationError as e:
            self.assertIn("@id' is a required property", str(e))
        else:
            self.fail("A ValidationError should be raised")
