from time import sleep
from unittest import TestCase

from splinter import Browser


class CMALoginTestCase(TestCase):

    def setUp(self):
        self.browser = Browser()

    def do_login(self):
        with self.browser as browser:
            browser.visit('http://admin.backstage.dev.globoi.com')
            sleep(2)

            browser.fill('username', 'icaro.medeiros')
            browser.fill('password', 'pass')

            button = browser.find_by_name('button')
            button.click()

    def test_login(self):
        self.do_login()
