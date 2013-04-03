from unittest import TestCase
from brainiak.utils.params import ParamDict, InvalidParam


class MockRequest():

    def __init__(self, **kw):
        self.kw = kw

    def get_argument(self, key, default_value):
        return self.kw.get(key, default_value)

    @property
    def arguments(self):
        return self.kw.keys()


class ParamsTestCase(TestCase):

    def test_initialize(self):
        params = ParamDict(context_name="context_name", class_name="class_name")
        self.assertIn("context_name", params)
        self.assertIn("class_name", params)
        self.assertEquals("context_name", params.get("context_name"))
        self.assertEquals("class_name", params.get("class_name"))

    def test_defaults_without_basic_params(self):
        params = ParamDict()
        self.assertEquals("invalid_context", params.get("context_name"))
        self.assertEquals("invalid_class", params.get("class_name"))
        self.assertEquals("invalid_instance", params.get("instance_id"))

    def test_override(self):
        params = ParamDict(class_name="default_class_name")
        params.override_with(MockRequest(class_name="overriden_class_name"))
        self.assertEquals("overriden_class_name", params.get("class_name"))

    def test_post_override_without_lang(self):
        params = ParamDict()
        params.override_with(MockRequest(lang="undefined"))
        self.assertEquals(params["lang"], "")

    def test_post_override_with_lang(self):
        params = ParamDict()
        params.override_with(MockRequest(lang="pt"))
        self.assertEquals(params["lang"], "pt")

    def test_override_with_invalid_argument(self):
        params = ParamDict(class_name="default_class_name")
        self.assertRaises(InvalidParam, params.override_with, MockRequest(inexistent_argument="whatever"))
