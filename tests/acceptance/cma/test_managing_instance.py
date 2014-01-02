# -*- coding: utf-8 -*-
from time import sleep

from helpers import SplinterTestCase


class ManageInstanceTestCase(SplinterTestCase):

    def do_login_and_enter_add_instance_form(self):
        create_assunto_eureka_buttons = self.browser.find_by_xpath("//h2[.='Eureka - Assunto Eureka']/following-sibling::a")
        create_assunto_eureka_buttons.first.click()
        sleep(2)

    def test_0_click_plus_button_open_add_instance_form(self):
        self.do_login_and_enter_add_instance_form()
        self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Adicionando Assunto Eureka']"))

    def test_1_slug_component(self):
        self.do_login_and_enter_add_instance_form()

        self.browser.type("rdfs:label", u"Acceptance test 01/01/2001")
        slug_element = self.browser.find_by_name("base:slug_topico")

        expected_slug_value = "acceptance-test-01-01-2001"
        self.assertEquals(expected_slug_value, slug_element.value)

    def click_on_button(self, name):
        button_create = self.browser.find_by_xpath(u"//button[contains(.,'{0}')]".format(name))
        button_create.click()

    def test_2_add_instance(self):
        self.do_login_and_enter_add_instance_form()

        self.browser.type("rdfs:label", u"Acceptance test 01/01/2001")
        self.browser.fill("base:descricao", "CMA acceptance test to validate Brainiak integration with the CMA")
        self.browser.fill("eureka:Keywords", "acceptance, test")

        suggest_element = self.browser.find_by_xpath("//p[.='Selecione']")
        suggest_element.click()

        suggest_input_search = self.browser.find_by_css("input.input-search")
        suggest_input_search.type("bio")

        suggest_option_biologia = self.browser.find_by_xpath("//p[.='Biologia']")
        suggest_option_biologia.click()

        self.click_on_button(u"Salvar")

        # After creating an instance, verify that we get back to the dashboard
        self.assertTrue(self.browser.is_element_present_by_xpath("//h2[.='Eureka - Assunto Eureka']"))

    def view_all(self):
        view_all_links = self.browser.find_by_xpath("//h2[.='Eureka - Assunto Eureka']/following-sibling::div/a[contains(.,'ver todos')]")
        view_all_links.first.click()

    def get_instance_in_list(self, search_pattern):

        while not self.browser.is_element_present_by_xpath(u"//p[.='Esta lista está vazia.']"):
            found_elements = self.browser.find_by_xpath(u"//tr/td/a[contains(.,'{0}')]".format(search_pattern))
            if not found_elements.is_empty():
                return found_elements.first

            # Go to next page
            next_buttons = self.browser.find_by_css("span.icons-right")
            next_buttons.first.click()
            sleep(1)

        raise RuntimeError(u"Instance with search pattern '{0}' not found".format(search_pattern))

    def test_3_search_for_created_instance(self):
        self.view_all()
        self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Listando Assunto Eureka']"))

        label_to_search = u"Acceptance"
        created_instance_element = self.get_instance_in_list(label_to_search)
        self.assertTrue(created_instance_element.text, u"Acceptance test 01/01/2001")

    def test_4_search_for_non_existent_instance_raises_exception(self):
        self.view_all()
        self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Listando Assunto Eureka']"))

        label_to_search = u"Nonexistent instance label"
        self.assertRaises(RuntimeError, self.get_instance_in_list, label_to_search)

    def test_5_edit_created_instance(self):
        self.view_all()

        created_instance_element = self.get_instance_in_list(u"Acceptance")
        created_instance_element.click()
        sleep(1)

        new_label = u"Acceptance tests with CMA 01/01/2001"

        self.browser.fill("rdfs:label", new_label)
        self.click_on_button(u"Salvar")
        self.assertFalse(self.browser.is_element_present_by_css("div.alert-error"))
        sleep(1)

        self.browser.back()
        edited_instance_element = self.get_instance_in_list(u"with CMA")
        self.assertTrue(edited_instance_element.text, new_label)

    def test_6_remove_created_and_edited_instance(self):
        edited_label_partial_value = u"with CMA"
        self.view_all()

        edited_instance_element = self.get_instance_in_list(edited_label_partial_value)
        edited_instance_element.click()
        sleep(1)

        self.click_on_button(u"Excluir")

        # Confirmation dialog opens
        confirmation_remove_buttons = self.browser.find_by_xpath("//div[@id='alert']//button[.='Excluir']")
        confirmation_remove_buttons.first.click()
