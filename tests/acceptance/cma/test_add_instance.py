from time import sleep

from helpers import do_login, SplinterTestCase


class AddInstanceTestCase(SplinterTestCase):

    def test_click_plus_button_open_add_instance_form(self):
        do_login(self.browser)
        sleep(3)
        self.assertTrue(self.browser.is_element_present_by_xpath("//h2[.='Eureka - Assunto Eureka']"))
        create_assunto_eureka_button = self.browser.find_by_xpath("//h2[.='Eureka - Assunto Eureka']/following-sibling::a")
        create_assunto_eureka_button.click()
        sleep(2)
        self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Adicionando Assunto Eureka']"))
