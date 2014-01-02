import os
from time import sleep
from unittest import TestCase

from splinter import Browser

ADMIN_USER = "semantica"
ADMIN_PASSWORD = os.getenv("SEMANTICA_USER_PASSWORD")

assert ADMIN_PASSWORD is not None, "Define environment variable SEMANTICA_USER_PASSWORD: export SEMANTICA_USER_PASSWORD=pass"

MAIN_PAGE = 'http://admin.backstage.dev.globoi.com'


def do_login(browser, user=ADMIN_USER, password=ADMIN_PASSWORD):
    browser.visit(MAIN_PAGE)
    sleep(1)

    browser.fill('username', user)
    browser.fill('password', password)

    button = browser.find_by_name('button')
    button.click()
    sleep(1)

# login_and_enter_dashboard()

browser = None

class SplinterTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = Browser()
        do_login(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def setUp(self):
        type(self).browser.visit(MAIN_PAGE)
        sleep(1)
