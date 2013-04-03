from unittest import TestCase
from brainiak.utils.params import ParamDict


class ParamsTestCase(TestCase):

    def test_initialize(self):
        params = ParamDict(bla="bla", foo="foo")
        self.assertIn("bla", params)
        self.assertEquals("bla", params.get("bla"))
