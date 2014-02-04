# -*- coding: utf-8 -*-

"""
Para executá-lo, basta rodar:
python check_deploy.py qa01

Onde <qa01> pode ser substituido por qualquer um dos ambientes:
- local, dev, qa01, qa02, stg e prod
"""

import inspect
import json
import sys
import time

import nose.tools as nose
import requests

brainiak_version = "2.4.4"
mercury_version = "1.2.6"

brainiak_endpoint = {
    "local": "http://0.0.0.0:5100/",
    "dev": "http://brainiak.semantica.dev.globoi.com/",
    "qa01": "http://brainiak.semantica.qa01.globoi.com/",
    "qa02": "http://brainiak.semantica.qa02.globoi.com/",
    "qa": "http://brainiak.semantica.qa.globoi.com/",
    "stg": "http://brainiak.semantica.globoi.com/",
    "prod": "http://brainiak.semantica.globoi.com/"
}


mercury_endpoint = {
    "local": "http://0.0.0.0:5200/",
    "dev": "http://cittavld44.globoi.com:8036/",
    "qa01": "http://cittavld45.globoi.com:8036/",
    "qa02": "http://api-semantica-be01.vb.qa02.globoi.com:8036/",
    "qa": "http://cittavld507.globoi.com:8036",
    "stg": "http://riovlb160.globoi.com:8036/",
    "prod": "http://riomp40lb14.globoi.com:8036/"
}

elastic_search_endpoint = {
    "dev": "http://esearch.dev.globoi.com/",
    "local": "http://localhost:9200/",
    "qa01": "http://esearch.qa01.globoi.com/",
    "qa02": "http://esearch.qa02.globoi.com/",
    "qa": "http://esearch.qa.globoi.com/",
    "stg": "http://esearch.globoi.com/",
    "prod": "http://esearch.globoi.com/"
}

solr_endpoint = {
    "dev": "http://master.solr.semantica.dev.globoi.com/",
    "local": "http://localhost:8984/",
    "qa01": "http://master.solr.semantica.qa01.globoi.com/",
    "qa02": "http://master.solr.semantica.qa02.globoi.com/",
    "qa": "http://master.solr.semantica.qa.globoi.com/",
    "stg": "http://master.solr.semantica.globoi.com/",
    "prod": "http://master.solr.semantica.globoi.com/"
}

proxies = {
    "stg": {"http": "http://proxy.staging.globoi.com:3128"},
    "qa": {"http": "http://proxy.qa.globoi.com:3128"}
}
#curl -i -X GET --proxy1.0 proxy.staging.globoi.com:3128 http://api.semantica.globoi.com/_status/check_activemq


class Checker(object):

    def __init__(self, environ):
        self.environ = environ
        self.proxies = proxies.get(environ, {})

    def delete(self, relative_url=""):
        url = "{0}{1}".format(self.endpoint, relative_url)
        return requests.delete(url, proxies=self.proxies)

    def get(self, relative_url=""):
        url = "{0}{1}".format(self.endpoint, relative_url)
        return requests.get(url, proxies=self.proxies)

    def put(self, relative_url="", filepath="", json_={}):
        if filepath:
            data = open(filepath, "r")
            json_ = json.load(data)
        payload = json.dumps(json_)
        url = "{0}{1}".format(self.endpoint, relative_url)
        return requests.put(url, proxies=self.proxies, data=payload)

    def post(self, relative_url="", filepath="", json_={}):
        if filepath:
            data = open(filepath, "r")
            json_ = json.load(data)
        payload = json.dumps(json_)
        url = "{0}{1}".format(self.endpoint, relative_url)
        return requests.post(url, proxies=self.proxies, data=payload)

    def _print_ok(self):
        sys.stdout.write("... OK \n")


class BrainiakChecker(Checker):

    def __init__(self, environ):
        Checker.__init__(self, environ)
        self.endpoint = brainiak_endpoint.get(environ)

    def check_activemq(self):
        sys.stdout.write("\nChecking ActiveMQ\n")
        response = self.get("_status/activemq")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        self._print_ok()

    def check_agregador_user_case(self):
        if environ == "local" or environ == "qa01":
            sys.stdout.write("\nChecking agregador user case - IGNORED ({0})\n".format(environ))
        else:
            sys.stdout.write("\nChecking agregador user case\n")
            response = self.get("g1/Materia/?p1=base:status_de_publicacao&o1=P&p2=g1:editoria_id&o2=268&sort_by=base:data_da_primeira_publicacao&sort_order=desc&p3=base:permalink")
            nose.assert_equal(response.status_code, 200)
            response_json = response.json()
            nose.assert_equal(response_json["@id"], u'g1:Materia')
            nose.assert_true(response_json["items"])
            expected_item_keys = [u'@id', u'base:data_da_primeira_publicacao', u'base:permalink', u'class_prefix', u'instance_prefix', u'resource_id', u'title']
            nose.assert_equal(sorted(response_json["items"][0].keys()), expected_item_keys)
            self._print_ok()

    def check_docs(self):
        if environ == "local":
            sys.stdout.write("\nChecking docs - ignore (local)\n")
        else:
            sys.stdout.write("\nChecking documentation\n")
            response = self.get("docs/")
            nose.assert_equal(response.status_code, 200)
            nose.assert_in("Brainiak API documentation!", response.text)
            self._print_ok()

    def check_healthcheck(self):
        sys.stdout.write("\nChecking healthcheck\n")
        response = self.get("healthcheck/")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(u'WORKING', response.text)
        self._print_ok()

    def check_instance_create(self):
        sys.stdout.write("\nChecking instance creation\n")
        # Remove if instance exist
        self.put("place/City/globoland", "new_city.json")
        self.delete("place/City/globoland")

        time.sleep(5)

        # SOLR read URL
        solr_host = solr_endpoint[self.environ]
        solr_relative_url = 'solr/select/?q=uri%3A%22http%3A%2F%2Fsemantica.globo.com%2Fplace%2FCity%2Fgloboland%22'
        solr_url = "{0}{1}".format(solr_host, solr_relative_url)

        # ElasticSearch read URL
        es_relative_url = 'semantica.place/http%3A%2F%2Fsemantica.globo.com%2Fplace%2FCity/http%3A%2F%2Fsemantica.globo.com%2Fplace%2FCity%2Fgloboland'
        es_host = elastic_search_endpoint[self.environ]
        es_url = "{0}{1}".format(es_host, es_relative_url)

        time.sleep(5)
        # Check if record does not exist in Solr
        solr_response = requests.get(solr_url, proxies=self.proxies)
        nose.assert_equal(solr_response.status_code, 200)
        nose.assert_in('numFound="0"', solr_response.text)

        # Check if instance does not exist in ElasticSearch
        es_response = requests.get(es_url, proxies=self.proxies)
        nose.assert_in(es_response.status_code, [404])

        # Add instance
        sys.stdout.write("\n-- check if <user_api_semantica> has write permission in Virtuoso if you get error 500 != 201\n",)
        response = self.put("place/City/globoland", "new_city.json")
        nose.assert_equal(response.status_code, 201)

        sys.stdout.write("-- try changing <check_instance_create> timeout if it fails\n")
        time.sleep(3)

        # Check if instance was written in Virtuoso
        response_after = self.get("place/City/globoland")
        nose.assert_equal(response_after.status_code, 200)
        nose.assert_in('"upper:fullName": "Globoland (RJ)"', response_after.text)

        # Check if instance was written in Solr
        solr_response = requests.get(solr_url, proxies=self.proxies)
        nose.assert_equal(solr_response.status_code, 200)
        sys.stdout.write("-- make sure ActiveMQ isn't overloaded, if you get an error related to numFound='0'\n",)
        nose.assert_in('numFound="1"', solr_response.text)
        nose.assert_in('<str name="label">Globoland: is the best</str>', solr_response.text)

        # Check if instance was written in ElasticSearch
        es_response = requests.get(es_url, proxies=self.proxies)
        nose.assert_equal(response_after.status_code, 200)

        self._print_ok()

    def check_instance_delete(self):
        sys.stdout.write("\nChecking instance deletion\n")
        self.put("place/City/globoland", "new_city.json")
        response = self.delete("place/City/globoland")
        nose.assert_equal(response.status_code, 204)
        response_after = self.get("place/City/globoland")
        nose.assert_equal(response_after.status_code, 404)
        self._print_ok()

    def check_redis(self):
        sys.stdout.write("\nChecking Redis\n")
        response = self.get("_status/cache")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        self._print_ok()

    def check_root(self):
        sys.stdout.write("\nChecking Root\n")
        response = self.get("?per_page=100")
        nose.assert_equal(response.status_code, 200)
        body = json.loads(response.text)
        expected_piece = {"resource_id": "upper", "@id": "http://semantica.globo.com/upper/", "title": "upper"}
        nose.assert_in(expected_piece, body["items"])
        self._print_ok()

    def check_sitemaps_user_case(self):
        if environ == "local":
            sys.stdout.write("\ncheck_sitemaps_user_case - ignore (local)\n")
        else:
            sys.stdout.write("\nChecking sitemaps user case\n")
            response = self.get("_/EventoMusicalAtomico?per_page=50000&p=base%3Aurl_do_permalink&graph_uri=http%3A%2F%2Fsemantica.globo.com%2FG1%2F&class_prefix=http%3A%2F%2Fsemantica.globo.com%2FG1%2F")
            nose.assert_equal(response.status_code, 200)
            response_json = response.json()
            nose.assert_equal(response_json["@id"], u'g1:EventoMusicalAtomico')
            expected_item_keys = [u'base:url_do_permalink', u'resource_id', u'title', u'class_prefix', u'instance_prefix', u'@id']
            nose.assert_equal(sorted(response_json["items"][0].keys()), sorted(expected_item_keys))
            self._print_ok()

    def check_status(self):
        sys.stdout.write("\nChecking status\n")
        response = self.get("_status")
        nose.assert_equal(response.status_code, 200)
        sys.stdout.write("\n-- if <check_status> breaks, check if Brainiak log doesn't contain (OSError) - Stale NFS file handle: 'locale' \n")
        nose.assert_in(u'FUNCIONANDO', response.text)
        self._print_ok()

    def check_suggest_sports_user_case(self):
        if environ == "local":
            sys.stdout.write("\ncheck_suggest_sports_user_case - ignore (local)\n")
        else:
            sys.stdout.write("\nChecking suggest sports user case\n")
            sys.stdout.write("\n-- run brainiak_sync for esportes/Equipe class, if <check_suggest_sports_user_case> breaks")
            PARAMS = {
                "search": {
                    "pattern": "flamengo",
                    "target": "esportes:tem_como_conteudo",
                    "fields": ["base:dados_buscaveis"],
                    "graphs": ["http://semantica.globo.com/esportes/"]
                },
                "response": {
                    "meta_fields": ["base:detalhe_da_cortina"],
                    "class_fields": ["base:thumbnail"]
                }
            }
            response = self.post("_suggest", json_=PARAMS)
            body = response.json()
            nose.assert_true(len(body["items"]))
            first_item = body["items"][0]
            second_item = body["items"][1]
            expected_keys = [u'rdfs:label', u'title', u'type_title', u'instance_fields', u'_type_title', u'class_fields', u'@id', u'@type']
            nose.assert_equal(second_item.keys(), expected_keys)
            titles = [first_item["title"], second_item["title"]]
            index = titles.index("Flamengo")
            flamengo_team = body["items"][index]
            nose.assert_equal(flamengo_team["title"], u"Flamengo")
            nose.assert_equal(flamengo_team["type_title"], u"Equipe")

            expected_instance_fields = [
                {
                    u'object_id': u'http://semantica.globo.com/esportes/esporte/1',
                    u'object_title': u'Futebol',
                    u'predicate_id': u'esportes:do_esporte',
                    u'predicate_title': u'Do esporte',
                    u'required': False
                },
                {
                    u'object_id': u'http://semantica.globo.com/esportes/categoria/4',
                    u'object_title': u'Futebol profissional',
                    u'predicate_id': u'esportes:da_categoria',
                    u'predicate_title': u'Da categoria',
                    u'required': False
                },
                {
                    u'object_id': u'http://semantica.globo.com/esportes/modalidade/1',
                    u'object_title': u'Futebol de campo',
                    u'predicate_id': u'esportes:da_modalidade',
                    u'predicate_title': u'Da modalidade',
                    u'required': False
                },
                {  # metafield
                    u'object_title': u'Flamengo',
                    u'predicate_id': u'esportes:nome_popular_sde',
                    u'predicate_title': u'Nome Popular no SDE',
                    u'required': True if self.environ != "dev" else False
                },
                {  # metafield
                    u'object_title': u'Flamengo ( Futebol / Futebol de campo / Profissional ) ',
                    u'predicate_id': u'esportes:composite',
                    u'predicate_title': u'Label de busca',
                    u'required': False
                }
            ]
            nose.assert_equal(sorted(flamengo_team["instance_fields"]), sorted(expected_instance_fields))
            nose.assert_true("base:thumbnail" in flamengo_team["class_fields"])

        self._print_ok()

    def check_version(self):
        sys.stdout.write("\nChecking /_version\n")
        response = self.get("_version")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(brainiak_version, response.text)
        self._print_ok()

    def check_virtuoso(self):
        sys.stdout.write("\nChecking Virtuoso Connection\n")
        response = self.get("_status/virtuoso")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        self._print_ok()


class MercuryChecker(Checker):

    def __init__(self, environ):
        Checker.__init__(self, environ)
        self.proxies = {}
        self.endpoint = mercury_endpoint.get(environ)

    def check_version(self):
        sys.stdout.write("\nChecking Mercury version\n")
        response = self.get("version/")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(mercury_version, response.text)
        self._print_ok()

    def check_healthcheck(self):
        sys.stdout.write("\nChecking healthcheck\n")
        response = self.get("healthcheck/")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(u'WORKING', response.text)
        self._print_ok()

    def check_status(self):
        sys.stdout.write("\nChecking status\n")
        response = self.get("status/")
        nose.assert_equal(response.status_code, 200)
        expected_piece = "Mercury is connected to event bus? YES"
        nose.assert_in(expected_piece, response.text)
        self._print_ok()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        environ = sys.argv[-1]
        if not environ in ["local", "dev", "qa01", "qa02", "stg", "prod"]:
            sys.stdout.write("Run:\n   python check_deploy.py <environ>\nWhere environ in [local, dev, qa01, qa02, stg, prod]")
            exit()
    else:
        sys.stdout.write("Run:\n   python check_deploy.py <environ>\nWhere environ in [local, dev, qa01, qa02, stg, prod]")
        exit()

    sys.stdout.write("[Checking Brainiak]")
    brainiak = BrainiakChecker(environ)
    brainiak_functions = [function() for name, function in inspect.getmembers(brainiak) if name.startswith("check")]
    sys.stdout.write("\n")

    sys.stdout.write("\n[Checking Mercury]")
    mercury = MercuryChecker(environ)
    [function() for name, function in inspect.getmembers(mercury) if name.startswith("check")]
    sys.stdout.write("\n")
