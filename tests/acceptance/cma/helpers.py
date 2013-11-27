import os
from time import sleep
from unittest import TestCase

from splinter import Browser

ADMIN_USER = "semantica"
ADMIN_PASSWORD = os.getenv("SEMANTICA_USER_PASSWORD")

assert ADMIN_PASSWORD is not None, "Define environment variable SEMANTICA_USER_PASSWORD: export SEMANTICA_USER_PASSWORD=pass"


def do_login(browser, user=ADMIN_USER, password=ADMIN_PASSWORD):
    browser.visit('http://admin.backstage.dev.globoi.com')
    sleep(2)

    browser.fill('username', user)
    browser.fill('password', password)

    button = browser.find_by_name('button')
    button.click()

# login_and_enter_dashboard()


class SplinterTestCase(TestCase):

    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.browser.quit()
