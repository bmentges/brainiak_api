import unittest

from tornado.web import HTTPError

from brainiak.instance.patch_instance import apply_patch


class PatchTestCase(unittest.TestCase):

    def test_apply_patch_one_replace_works(self):
        instance_data = {
            u'http://on.to/name': u'Flipper',
            u'http://on.to/age': 4
        }
        patch_list = [
            {
                u'path': u'http://on.to/age',
                u'value': 5,
                u'op': u'replace'
            }
        ]
        computed = apply_patch(instance_data, patch_list)
        expected = {
            u'http://on.to/name': u'Flipper',
            u'http://on.to/age': 5
        }
        self.assertEqual(computed, expected)

    def test_apply_patch_with_wrong_keys(self):
        instance_data = {}
        patch_list = [
            {
                'wrong key': 'any value'
            }
        ]
        with self.assertRaises(HTTPError) as error:
            apply_patch(instance_data, patch_list)
        msg = str(error.exception)
        expected = 'HTTP 400: Bad Request (Incorrect patch item. Every object in the list must contain the following keys: op, path and value)'
        self.assertEqual(msg, expected)
        
