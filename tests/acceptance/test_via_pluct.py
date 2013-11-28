# -*- coding: utf-8 -*-

from unittest import TestCase
from pluct.request import Credentials
from pluct.api import Api

API_ENDPOINT = "http://brainiak.semantica.dev.globoi.com"
#API_ENDPOINT = "http://localhost:5100"

DEV_CREDENTIALS = Credentials("http://accounts.backstage.dev.globoi.com/token",
                              "U6fvLX9xb9gjJm15/h33eA==",
                              "FcmspQN5uiWfMK2FpPzZgg==")

EUREKA_CREDENTIALS = Credentials("http://accounts.backstage.dev.globoi.com/token",
                                 "FSezuthPogii6n7MvrK1hg==",
                                 "8Np3XRO3PkYptg2w/mxf9Q==")


class ValidateDirectResources(TestCase):

    def test_valid_root(self):
        api = Api(API_ENDPOINT)
        self.assertTrue(api.root.is_valid())


class ValidateResourcesViaBackstage(TestCase):

    def test_valid_root_with_oauth(self):
        api = Api("http://brainiak.backstage.dev.globoi.com", DEV_CREDENTIALS)
        self.assertTrue(api.root.is_valid())
