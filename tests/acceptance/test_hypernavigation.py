# -*- coding: utf-8 -*-

from unittest import TestCase
from pluct.resource import get

API_ENDPOINT = "http://brainiak.semantica.dev.globoi.com"


class AcceptListContexts(TestCase):

    def test_successful_list_context(self):
        pass


if __name__ == '__main__':
    proxy = get(API_ENDPOINT)
