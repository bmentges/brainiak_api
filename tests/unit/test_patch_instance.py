import unittest

from tornado.web import HTTPError

from brainiak.instance.patch_instance import apply_patch


class PatchTestCase(unittest.TestCase):

    def test_apply_patch_replace_succeeds(self):
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

    def test_apply_patch_with_wrong_keys_raises_400(self):
        instance_data = {}
        patch_list = [
            {
                'wrong key': 'any value'
            }
        ]
        with self.assertRaises(HTTPError) as error:
            apply_patch(instance_data, patch_list)
        msg = str(error.exception)
        expected = "HTTP 400: Bad Request (Incorrect patch item. Every object in the list must contain the following keys: ['op', 'path'])"
        self.assertEqual(msg, expected)

    def test_apply_patch_remove_succeeds(self):
        instance_data = {
            'http://on.to/name': u'Flipper',
            'http://on.to/weight': 200.0
        }
        patch_list = [
            {
                u'path': 'http://on.to/weight',
                u'op': u'remove'
            }
        ]
        computed = apply_patch(instance_data, patch_list)
        expected = {
            u'http://on.to/name': u'Flipper',
        }
        self.assertEqual(computed, expected)

    def test_apply_patch_remove_succeeds_for_expanded_uri(self):
        instance_data = {
            'http://dbpedia.org/ontology/name': u'Francis'
        }
        patch_list = [
            {
                u'path': 'dbpedia:name',
                u'op': u'remove'
            }
        ]
        computed = apply_patch(instance_data, patch_list)
        expected = {}
        self.assertEqual(computed, expected)

    def test_apply_patch_add_inexistent_data_succeeds(self):
        instance_data = {
        }
        patch_list = [
            {
                u'path': 'http://on.to/children',
                u'op': u'add',
                u'value': u'Mary'
            }
        ]
        computed = apply_patch(instance_data, patch_list)
        expected = {
            u'http://on.to/children': [u'Mary'],
        }
        self.assertEqual(computed, expected)
        
    def test_apply_patch_add_list_data_succeeds(self):
        instance_data = {
            'http://on.to/children': ['Dave', 'Eric']
        }
        patch_list = [
            {
                u'path': 'http://on.to/children',
                u'op': u'add',
                u'value': [u'Mary', u'John']
            }
        ]
        computed = apply_patch(instance_data, patch_list)
        expected = {
            u'http://on.to/children': ['Dave', 'Eric', 'John', 'Mary'],
        }
        self.assertEqual(computed, expected)
