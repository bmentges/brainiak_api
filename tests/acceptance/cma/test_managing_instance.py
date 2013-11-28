# -*- coding: utf-8 -*-
from time import sleep

from helpers import do_login, SplinterTestCase


class AddInstanceTestCase(SplinterTestCase):

    def do_login_and_enter_add_instance_form(self):
        do_login(self.browser)
        sleep(3)
        create_assunto_eureka_button = self.browser.find_by_xpath("//h2[.='Eureka - Assunto Eureka']/following-sibling::a")
        create_assunto_eureka_button.click()
        sleep(2)

    #def test_0_click_plus_button_open_add_instance_form(self):
    #    self.do_login_and_enter_add_instance_form()
    #    self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Adicionando Assunto Eureka']"))

    #def test_1_slug_component(self):
    #    self.do_login_and_enter_add_instance_form()

    #    self.browser.type("rdfs:label", u"Teste de aceitação 01/01/2001")
    #    slug_element = self.browser.find_by_name("base:slug_topico")

    #    expected_slug_value = "teste-de-aceitacao-01-01-2001"
    #    self.assertEquals(expected_slug_value, slug_element.value)

    def click_on_save_button(self):
        button_create = self.browser.find_by_xpath("//button[contains(.,'Salvar')]")
        button_create.click()

    #def test_2_add_instance(self):
    #    self.do_login_and_enter_add_instance_form()

    #    self.browser.type("rdfs:label", u"Teste de aceitação 01/01/2001")
    #    self.browser.fill("base:descricao", "Teste de aceitacao CMA para validar integracao do Brainiak com o CMA")
    #    self.browser.fill("eureka:Keywords", "aceitacao, teste")

    #    suggest_element = self.browser.find_by_xpath("//p[.='Selecione']")
    #    suggest_element.click()

    #    suggest_input_search = self.browser.find_by_css("input.input-search")
    #    suggest_input_search.type("bio")

    #    suggest_option_biologia = self.browser.find_by_xpath("//p[.='Biologia']")
    #    suggest_option_biologia.click()


    #    # After creating an instance, verify that we get back to the dashboard
    #    self.assertTrue(self.browser.is_element_present_by_xpath("//h2[.='Eureka - Assunto Eureka']"))

    def view_all(self):
        view_all_links = self.browser.find_by_xpath("//h2[.='Eureka - Assunto Eureka']/following-sibling::div/a[contains(.,'ver todos')]")
        view_all_links.first.click()

    def search_for_instance(self, search_pattern):
        self.browser.fill("search-pattern", search_pattern)

        search_button = self.browser.find_by_name("search")
        search_button.click()

    #def test_3_search_for_created_instance(self):
    #    do_login(self.browser)

    #    self.view_all()
    #    self.assertTrue(self.browser.is_element_present_by_xpath("//h1[.='Listando Assunto Eureka']"))

    #    self.search_for_instance(u"aceitação")
    #    self.assertTrue(self.browser.is_element_present_by_xpath("//tr/td/a[contains(.,'aceitação')]"))

    def test_4_edit_created_instance(self):
        do_login(self.browser)

        self.view_all()
        self.search_for_instance(u"aceitação")

        created_instance_on_search_result = self.browser.find_by_xpath("//tr/td/a[contains(.,'aceitação')]")
        created_instance_on_search_result.click()
        sleep(1)

        self.browser.fill("rdfs:label", u"Teste de aceitação CMA 01/01/2001")

        self.click_on_save_button()

        # TODO salvar, back, busca por u"aceitação CMA"

    def test_5_remove_created_and_edited_instance(self):
        pass
