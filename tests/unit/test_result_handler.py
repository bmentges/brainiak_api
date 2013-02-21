import unittest

# from brainiak.result_handler import CardinalityResultHandler, \
#     PredicateResultHandler, get_one_value, get_ranges_graphs, simplify_dict, \
#     parse_label_and_type, is_result_empty, filter_values, lang_dict
#
# from tests.fixtures import CLASS, PREDICATE, CARDINALITY, \
#     CARDINALITY_WITH_ENUMERATED_VALUE, \
#     RANGES_DICT, SIMPLIFIED_RANGE_GRAPHS, \
#     PREDICATE_DICT_ORIGINAL, SIMPLIFIED_PREDICATE_DICT, \
#     EMPTY_GRAPHS_RANGES_DICT, RESULT_DICT_WITH_LANG, FINAL_CLASS_PERSON

#
# class ResultHandlerTestCase(unittest.TestCase):
#
#     def test_get_result(self):
#         expected = "http://test.domain.com/G1/Video"
#         self.assertEquals(expected, get_one_value(CLASS, "videoClass"))
#
#     def test_get_result_empty(self):
#         self.assertFalse(get_one_value(CLASS, "chave_inexistente"))
#
#     def test_is_result_empty_returns_true(self):
#         empty_result_dict = {u'head': {u'link': [], u'vars': [u'graph', u'p', u'o']},
#                              u'results': {u'distinct': False, u'bindings': [], u'ordered': True}}
#         self.assertTrue(is_result_empty(empty_result_dict))
#
#     def test_is_result_empty_returns_false(self):
#         empty_result_dict = {u'head': {u'link': [], u'vars': [u'graph', u'p', u'o']},
#                              u'results': {u'distinct': False, u'bindings': ["teste1", "teste2"], u'ordered': True}}
#         self.assertFalse(is_result_empty(empty_result_dict))
#
#     def test_filter_values_with_lang(self):
#         expected = ["Pessoa"]
#         result = filter_values(RESULT_DICT_WITH_LANG, "label")
#         self.assertEquals(expected, result)
#
#     def test_lang_dict(self):
#         result_list = ["Person@en", "Pessoa"]
#         expected = {"en": "Person", "pt": "Pessoa"}
#         result = lang_dict(result_list)
#         self.assertEquals(expected, result)
#
#
# class CardinalityResultHandlerTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.result_handler = CardinalityResultHandler(CARDINALITY)
#
#     def test_get_cardinalities(self):
#         expected = {
#             "http://test.domain.com/base/data_de_criacao_do_conteudo": {
#                 "http://www.w3.org/2001/XMLSchema#dateTime": {
#                     "min": "1",
#                     "max": "1"
#                 }
#             },
#             "http://test.domain.com/base/status_de_publicacao": {
#                 "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral": {
#                     "min": "1",
#                     "max": "1"
#                 }
#             },
#             "http://test.domain.com/base/pertence_ao_produto": {
#                 "http://test.domain.com/base/Produto": {
#                     "min": "1"
#                 }
#             },
#             "http://www.w3.org/2000/01/rdf-schema#label": {
#                 "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral": {
#                     "min": "1",
#                     "max": "1"
#                 }
#             }
#         }
#
#         self.assertEquals(expected, self.result_handler.get_cardinalities())
#
#
# class CardinalityResultHandlerWithEnumerationTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.result_handler = CardinalityResultHandler(CARDINALITY_WITH_ENUMERATED_VALUE)
#
#     def test_get_cardinalities(self):
#         expected = {'http://test.domain.com/predicate_with_enumerated_value':
#                         {'http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral': {},
#                          'options': [{'Masculino': 'Sexo'}]}}
#         self.assertEquals(expected, self.result_handler.get_cardinalities())
#
#
# class PredicateResultHandlerTestCase(unittest.TestCase):
#
#     def setUp(self):
#         class_uri = "http://test.domain.com/person/Person"
#         self.result_handler = PredicateResultHandler(class_uri, RESULT_DICT_WITH_LANG, PREDICATE, CARDINALITY)
#         self.maxDiff = None
#
#     def test_get_complete_dict(self):
#         expected = FINAL_CLASS_PERSON
#         result = self.result_handler.get_complete_dict()
#         self.assertEquals(expected, result)
#
#
# class SimplifyPredicateDictTestCase(unittest.TestCase):
#
#     def test_simplifiy_dict(self):
#         expected = SIMPLIFIED_PREDICATE_DICT
#         result = simplify_dict(PREDICATE_DICT_ORIGINAL)
#         self.assertEquals(expected, result)
#
#     def test_get_range_graphs_empty(self):
#         expected = []
#         result = get_ranges_graphs(EMPTY_GRAPHS_RANGES_DICT)
#         self.assertEquals(expected, result)
#
#     def test_get_range_graphs(self):
#         expected = SIMPLIFIED_RANGE_GRAPHS
#         result = get_ranges_graphs(RANGES_DICT)
#         self.assertEquals(expected, result)
#
#
# class GetOneTestCase(unittest.TestCase):
#
#     response = {u'head': {u'link': [], u'vars': [u'graph', u'videoClass', u'program']},
#                 u'results': {u'distinct': False, u'bindings':
#                              [{u'videoClass': {u'type': u'uri', u'value': u'http://test.domain.com/G1/Video'}}],
#                              u'ordered': True}}
#
#     def test_get_result(self):
#         computed = get_one_value(self.response, "videoClass")
#         expected = "http://test.domain.com/G1/Video"
#         self.assertEquals(computed, expected)
#
#     def test_get_result_empty(self):
#         computed = get_one_value(self.response, "chave_inexistente")
#         expected = False
#         self.assertEquals(computed, expected)
#
#
# def test_simplify_label_type_dict():
#     sparql_response = {
#         "head": {
#             "link": [],
#             "vars": ["label", "type_label"]},
#         "results": {
#             "distinct": False,
#             "ordered": True,
#             "bindings": [
#             {"label": {"type": "literal", "value": "Rio de Janeiro"},
#              "type_label": {"type": "literal", "value": "Cidade"}}
#             ]
#         }
#     }
#     expected = {"type_label": "Cidade", "label": "Rio de Janeiro"}
#     response = parse_label_and_type(sparql_response)
#     assert expected == response
#
#
# def test_simplify_label_type_dict_with_empty_bindings():
#     sparql_response = {
#         "head": {
#             "link": [],
#             "vars": ["label", "type_label"]
#         },
#         "results": {
#             "distinct": False,
#             "ordered": True,
#             "bindings": []
#         }
#     }
#     expected = {}
#     response = parse_label_and_type(sparql_response)
#     assert expected == response
