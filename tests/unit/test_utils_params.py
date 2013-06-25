from unittest import TestCase
from brainiak.prefixes import ROOT_CONTEXT
from brainiak.settings import URI_PREFIX
from brainiak.utils.params import ParamDict, InvalidParam, DefaultParamsDict, LIST_PARAMS, valid_pagination, INSTANCE_PARAMS, CACHE_PARAMS
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
        self.assertEquals(None, params.get("context_name"))
        self.assertEquals(None, params.get("class_name"))
        self.assertEquals(None, params.get("instance_id"))

    def test_defaults_with_basic_params(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name='ctx_name', class_name='klass')
        self.assertEquals('ctx_name', params.get("context_name"))
        self.assertEquals('klass', params.get("class_name"))

    def test_override(self):
        handler = MockHandler(querystring="context_name=dbpedia&class_name=overriden_class_name")
        params = ParamDict(handler, context_name='dbpedia', class_name="default_class_name", class_prefix=None)
        self.assertEquals("overriden_class_name", params.get("class_name"))

    def test_post_override_without_lang(self):
        handler = MockHandler(querystring="lang=undefined")
        params = ParamDict(handler, lang=None)
        self.assertEquals(params["lang"], "")

    def test_post_override_with_lang(self):
        handler = MockHandler(querystring="lang=pt")
        params = ParamDict(handler, lang=None)
        self.assertEquals(params["lang"], "pt")

    def test_expand_curie(self):
        handler = MockHandler(querystring="graph_uri=glb")
        params = ParamDict(handler, graph_uri=None)
        self.assertEquals(params["graph_uri"], "http://semantica.globo.com/")

    def test_post_override_with_sort_order(self):
        handler = MockHandler(querystring="sort_order=asc")
        params = ParamDict(handler, **LIST_PARAMS)
        self.assertEquals(params["sort_order"], "ASC")

    def test_post_override_without_sort_order(self):
        handler = MockHandler()
        params = ParamDict(handler, **LIST_PARAMS)
        self.assertEquals(params["sort_order"], "ASC")

    def test_post_override_with_sort_include_empty(self):
        handler = MockHandler(querystring="sort_include_empty=0")
        params = ParamDict(handler, **LIST_PARAMS)
        self.assertEquals(params["sort_include_empty"], "0")

    def test_post_override_without_sort_include_empty(self):
        handler = MockHandler()
        params = ParamDict(handler, **LIST_PARAMS)
        self.assertEquals(params["sort_include_empty"], "1")

    def test_post_override_with_page(self):
        handler = MockHandler(querystring="page=3")
        params = ParamDict(handler, **LIST_PARAMS)
        # The Class will be responsible to decrement the page index to be compatible with virtuoso's indexing convention
        self.assertEquals(params["page"], "2")

    def test_override_with_invalid_argument(self):
        handler = MockHandler(querystring="inexistent_argument=whatever")
        self.assertRaises(InvalidParam, ParamDict, handler, context_name='dbpedia', class_name="default_class_name", class_prefix=None)

    def test_class_uri_from_context_and_class(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name="dbpedia", class_name="Actor", class_uri=None)
        self.assertEquals(params["class_uri"], "http://dbpedia.org/ontology/Actor")

    def test_class_uri_from_context_and_class_with_class_uri(self):
        handler = MockHandler(querystring="class_uri=http://someprefix/someClass")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor')
        self.assertEquals(params["class_uri"], "http://someprefix/someClass")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(querystring="class_prefix=http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor', class_prefix=None)
        self.assertEquals(params["class_prefix"], "http://someprefix/")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(querystring="class_prefix=http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor', class_prefix=None)
        self.assertEquals(params["class_uri"], "http://someprefix/Actor")

    def test_class_uri_from_context_and_class_with_class_prefix(self):
        handler = MockHandler(querystring="class_prefix=http://someprefix/")
        params = ParamDict(handler, context_name='dbpedia', class_name='Actor', class_prefix=None)
        self.assertEquals(params["class_uri"], "http://someprefix/Actor")

    def test_context_name_affects_class_prefix_and_graph_uri(self):
        handler = MockHandler()
        params = ParamDict(handler, context_name='dbpedia')
        self.assertEquals(params["class_prefix"], "http://dbpedia.org/ontology/")
        self.assertEquals(params["graph_uri"], "http://dbpedia.org/ontology/")

    def test_context_class_instance_define_instance_uri(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='dbpedia', class_name='klass', instance_id='inst',
                           graph_uri=None, instance_uri=None, instance_prefix=None)
        self.assertEquals(params["instance_uri"], "http://dbpedia.org/ontology/klass/inst")

    def test_pagination_validation(self):
        self.assertTrue(valid_pagination(total=1, page=0, per_page=10))
        self.assertTrue(valid_pagination(total=1, page=0, per_page=1))
        self.assertFalse(valid_pagination(total=10, page=1, per_page=10))
        self.assertFalse(valid_pagination(total=1, page=1, per_page=1))


class OrderingTestCase(TestCase):

    def test_ctx_class_inst_id(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='person', class_name='Gender', instance_id="Male",
                           **INSTANCE_PARAMS)
        self.assertEquals(params["instance_uri"], "http://semantica.globo.com/person/Gender/Male")

    def test_class_prefix(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='dbpedia', class_name='klass', class_prefix="http://this/should/be/used/")
        self.assertEquals(params["class_uri"], "http://this/should/be/used/klass")

    def test_class_uri_and_prefix(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='dbpedia', class_name='klass',
                           class_uri="http://this/should/be/used",
                           class_prefix="http://this/is/less/important/than/class_uri")
        self.assertEquals(params["class_uri"], "http://this/should/be/used")

    def test_instance_prefix(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='dbpedia', class_name='klass', instance_id='inst',
                           instance_prefix="http://this/should/be/used/")
        self.assertEquals(params["instance_uri"], "http://this/should/be/used/inst")

    def test_instance_uri_and_prefix(self):
        handler = MockHandler()
        params = ParamDict(handler,
                           context_name='dbpedia', class_name='klass', instance_id='inst',
                           instance_uri="http://this/should/be/used",
                           instance_prefix="http://this/is/less/important/than/instance_uri")
        self.assertEquals(params["instance_uri"], "http://this/should/be/used")


class SpecificParamsDictTestCase(TestCase):

    def test_cache_params_definitions(self):
        self.assertEqual(CACHE_PARAMS.get("purge"), "0")
