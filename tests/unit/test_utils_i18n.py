import unittest

from mock import patch

from brainiak.utils import i18n


class TranslationTestCase(unittest.TestCase):

    def test_underscore_is_defined(self):
        self.assertEqual(i18n._, i18n.translate)

    def test_translate_to_portuguese(self):
        translated_string = i18n.translate(u"WORKING", lang="pt")
        expected_string = u"FUNCIONANDO"
        self.assertEqual(translated_string, expected_string)

    def test_translate_to_default_english(self):
        translated_string = i18n.translate(u"WORKING", lang="en")
        expected_string = u"WORKING"
        self.assertEqual(translated_string, expected_string)
