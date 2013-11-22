# -*- coding: utf-8 -*-

from unittest import TestCase
from brainiak.utils.client import add_instance_with_url, del_instance, fetch_page

API_ENDPOINT = 'http://localhost:5100'


class ManageInstance(TestCase):

    def test_add_and_delete(self):
        data = {'upper:name': u'Eurásia'}
        url = API_ENDPOINT + '/place/Continent/Eurasia'

        status_code, err = add_instance_with_url(url, data)
        self.assertEqual(status_code, 201)

        status_code, body = fetch_page(url)
        self.assertEqual(status_code, 200)

        status_code, err = del_instance(url)
        self.assertEqual(status_code, 204)
