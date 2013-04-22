from unittest import TestCase
from brainiak.handlers import ListServiceParams
from brainiak.prefixes import ROOT_CONTEXT
from brainiak.settings import URI_PREFIX
from brainiak.utils.params import ParamDict, InvalidParam, DefaultParamsDict, LIST_PARAMS
from tests.mocks import MockHandler


class DefaultParamsTest(TestCase):

    def test_add_dicts(self):
        a = DefaultParamsDict(a=1)
        b = DefaultParamsDict(b=2)
        a_b = a + b
        b_a = dict(a=1, b=2)
        self.assertEqual(a_b, b_a)
        self.assertEqual(a, {"a": 1})
        self.assertEqual(b, {"b": 2})


class ParamsTestCase(TestCase):

    def test_initialize(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name="context_name", class_name="class_name")
        self.assertIn("context_name", params)
        self.assertIn("class_name", params)
        self.assertEquals("context_name", params.get("context_name"))
        self.assertEquals("class_name", params.get("class_name"))

    def test_root_context(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name=ROOT_CONTEXT)
        self.assertEquals(URI_PREFIX, params.get("graph_uri"))

    def test_defaults_without_basic_params(self):
        handler = MockHandler()
        params = ParamDict(handler)
        self.assertEquals("invalid_context", params.get("context_name"))
        self.assertEquals("invalid_class", params.get("class_name"))
        self.assertEquals("invalid_instance", params.get("instance_id"))

    def test_override(self):
        handler = MockHandler(class_name="overriden_class_name")
        params = ParamDict(handler, class_name="default_class_name")
        self.assertEquals("overriden_class_name", params.get("class_name"))

    def test_post_override_without_lang(self):
        handler = MockHandler(lang="undefined")
        params = ParamDict(handler)
        self.assertEquals(params["lang"], "")

    def test_post_override_with_lang(self):
        handler = MockHandler(lang="pt")
        params = ParamDict(handler)
        self.assertEquals(params["lang"], "pt")

    def test_expand_curie(self):
        handler = MockHandler(graph_uri="glb")
        params = ParamDict(handler)
        self.assertEquals(params["graph_uri"], "http://semantica.globo.com/")

    def test_post_override_with_sort_order(self):
        handler = MockHandler(sort_order="asc")

        class ListParamDict(ParamDict):
            extra_params = LIST_PARAMS

        params = ListParamDict(handler)
        self.assertEquals(params["sort_order"], "ASC")

    def test_post_override_without_sort_order(self):
        handler = MockHandler(sort_order="")

        class ListParamDict(ParamDict):
            extra_params = LIST_PARAMS

        params = ListParamDict(handler)
        self.assertEquals(params["sort_order"], "")

    def test_post_override_with_sort_include_empty(self):
        handler = MockHandler(sort_include_empty="0")

        class ListParamDict(ParamDict):
            extra_params = LIST_PARAMS

        params = ListParamDict(handler)
        self.assertEquals(params["sort_include_empty"], "0")

    def test_post_override_without_sort_include_empty(self):
        handler = MockHandler()

        class ListParamDict(ParamDict):
            extra_params = LIST_PARAMS

        params = ListParamDict(handler)
        self.assertEquals(params["sort_include_empty"], "1")

    def test_post_override_with_page(self):
        handler = MockHandler(page="3")
        params = ListServiceParams(handler)
        # The Class will be responsible to decrement the page index to be compatible with virtuoso's indexing convention
        self.assertEquals(params["page"], "2")

    def test_override_with_invalid_argument(self):
        handler = MockHandler(inexistent_argument="whatever")
        self.assertRaises(InvalidParam, ParamDict, handler, class_name="default_class_name")

    def test_class_uri_from_context_and_class(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_uri"], "http://dbpedia.org/ontology/Actor")

    def test_class_uri_from_context_and_class_with_class_uri(self):
        handler = MockHandler(class_uri="http://someprefix/someClass")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_uri"], "http://someprefix/someClass")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(class_prefix="http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_prefix"], "http://someprefix/")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(class_prefix="http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_uri"], "http://someprefix/Actor")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(class_prefix="http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_uri"], "http://someprefix/Actor")

    def test_context_name_affects_class_prefix_and_graph_uri(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name='dbpedia')
        self.assertEquals(params["class_prefix"], "http://dbpedia.org/ontology/")
        self.assertEquals(params["graph_uri"], "http://dbpedia.org/ontology/")

    def test_context_class_instance_define_instance_uri(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name='dbpedia', class_name='klass', instance_id='inst')
        self.assertEquals(params["instance_uri"], "http://dbpedia.org/ontology/klass/inst")
