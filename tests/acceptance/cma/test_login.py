from time import sleep

from helpers import do_login, SplinterTestCase


class CMALoginTestCase(SplinterTestCase):

    def test_wrong_login(self):
        do_login(self.browser, user="user", password="password")
        self.assertTrue(self.browser.is_element_present_by_css("div.error"))

    def test_successful_login_goes_to_dashboard(self):
        do_login(self.browser)
        sleep(3)
        self.assertTrue(self.browser.is_element_present_by_xpath("//h2[.='Eureka - Assunto Eureka']"))
