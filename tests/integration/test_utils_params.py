import unittest

from tornado.web import Application

from brainiak.handlers import BrainiakRequestHandler
from brainiak.utils.params import ParamDict
from tests.mocks import MockRequest
from tests.tornado_cases import TornadoAsyncHTTPTestCase


class TranslationTestCase(unittest.TestCase):

    class Handler(BrainiakRequestHandler):

        def get(self):
            locale.load_gettext_translations(directory="locale", domain="brainiak")
            user_locale = self.get_browser_locale()
            _ = user_locale.translate
            self.finalize(_("WORKING"))

    def get_app(self):
        return Application([('/', self.Handler)],
                           log_function=lambda x: None)

    def test_translate_to_portuguese(self):
        headers = {"Accept-Language": "pt_BR;q=0.8,en;q=0.2"}
        request = MockRequest(headers=headers)
        handler = self.Handler(self.get_app(), request)
        params = ParamDict(handler)
        translated_string = params.translate(u"WORKING")
        expected_string = u"FUNCIONANDO"
        self.assertEqual(translated_string, expected_string)

    def test_translate_to_default_english(self):
        request = MockRequest()
        handler = self.Handler(self.get_app(), request)
        params = ParamDict(handler)
        translated_string = params.translate(u"WORKING")
        expected_string = u"WORKING"
        self.assertEqual(translated_string, expected_string)
