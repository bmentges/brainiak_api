from time import sleep
from unittest import TestCase

from splinter import Browser

from helpers import do_login


class CMALoginTestCase(TestCase):

    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.browser.quit()

    def test_wrong_login(self):
        do_login(self.browser, "user", "password")
        self.assertTrue(self.browser.is_element_present_by_css("div .error"))

    def test_successful_login_goes_to_dashboard(self):
        do_login(self.browser, "icaro.medeiros", "pass") # please change using your password while we dont have a test user
        sleep(3)
        self.assertTrue(self.browser.is_element_present_by_css("div .dashboard"))
