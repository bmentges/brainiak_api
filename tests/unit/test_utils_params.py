from unittest import TestCase
from brainiak.handlers import ListServiceParams
from brainiak.prefixes import ROOT_CONTEXT
from brainiak.settings import URI_PREFIX
from brainiak.utils.params import ParamDict, InvalidParam, DefaultParamsDict


class MockHandler():

    def __init__(self, **kw):
        self.kw = kw

    def get_argument(self, key):
        return self.kw.get(key)

    @property
    def request(self):
        class Dummy(object):
            @property
            def arguments(inner_self):
                return self.kw.keys()

        d = Dummy()
        return d


class DefaultParamsTest(TestCase):
    def test_add_dicts(self):
        a = DefaultParamsDict(a=1)
        b = DefaultParamsDict(b=2)
        a_b = a + b
        b_a = dict(a=1, b=2)
        self.assertEqual(a_b, b_a)


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

    def test_post_override_with_page(self):
        handler = MockHandler(page="3")
        params = ListServiceParams(handler)
        # The Class will be responsible to decrement the page index to be compatible with virtuoso's indexing convention
        self.assertEquals(params["page"], "2")

    def test_override_with_invalid_argument(self):
        handler = MockHandler(inexistent_argument="whatever")
        self.assertRaises(InvalidParam, ParamDict, handler, class_name="default_class_name")
