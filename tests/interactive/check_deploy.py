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

version = "master"

brainiak_endpoint = {
    "local": "http://0.0.0.0:5100/",
    "dev": "http://api.semantica.dev.globoi.com/",
    "qa01": "http://api.semantica.qa01.globoi.com/",
    "qa02": "http://api.semantica.qa01.globoi.com/",
    "stg": "http://api.semantica.globoi.com/",
    "prod": "http://api.semantica.globoi.com/"
}

mercury_endpoint = {
    "local": "http://0.0.0.0:5200/",
    "dev": "http://cittavld44.globoi.com:8036/",
    "qa01": "http://cittavld45.globoi.com:8036/",
    "qa02": "http://api-semantica-be01.vb.qa02.globoi.com:8036/",
    "stg": "http://riovlb160.globoi.com:8036/",
    "prod": "http://riomp40lb14.globoi.com:8036/"
}

elastic_search_endpoint = {
    "dev": "http://esearch.dev.globoi.com/",
    "local": "http://localhost:9200/",
    "qa01": "http://esearch.qa01.globoi.com/",
    "qa02": "http://esearch.qa02.globoi.com/",
    "stg": "http://esearch.globoi.com/",
    "prod": "http://esearch.globoi.com/"
}

solr_endpoint = {
    "dev": "http://master.solr.semantica.dev.globoi.com/",
    "local": "http://localhost:8984/",
    "qa01": "http://master.solr.semantica.qa01.globoi.com/",
    "qa02": "http://master.solr.semantica.qa02.globoi.com/",
    "stg": "http://master.solr.semantica.globoi.com/",
    "prod": "http://master.solr.semantica.globoi.com/"
}

proxies = {
    "stg": {"http": "proxy.staging.globoi.com:3128"}
}


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

    def put(self, relative_url="", filepath=""):
        fp = open(filepath, "r")
        payload = json.dumps(json.load(fp))
        url = "{0}{1}".format(self.endpoint, relative_url)
        return requests.put(url, proxies=self.proxies, data=payload)


class BrainiakChecker(Checker):

    def __init__(self, environ):
        Checker.__init__(self, environ)
        self.endpoint = brainiak_endpoint.get(environ)

    def check_healthcheck(self):
        response = self.get("healthcheck/")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(u'WORKING', response.text)
        sys.stdout.write("\ncheck_healthcheck - pass")

    def check_virtuoso(self):
        response = self.get("_status/virtuoso")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        sys.stdout.write("\ncheck_virtuoso - pass")

    def check_activemq(self):
        response = self.get("_status/activemq")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        sys.stdout.write("\ncheck_activemq - pass")

    def check_redis(self):
        response = self.get("_status/cache")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in("SUCCEED", response.text)
        sys.stdout.write("\ncheck_redis - pass")

    def check_root(self):
        response = self.get()
        nose.assert_equal(response.status_code, 200)
        body = json.loads(response.text)
        expected_piece = {"resource_id": "upper", "@id": "http://semantica.globo.com/upper/", "title": "upper"}
        nose.assert_in(expected_piece, body["items"])
        sys.stdout.write("\ncheck_root - pass")

    def check_version(self):
        response = self.get("_version")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(version, response.text)
        sys.stdout.write("\ncheck_version - pass")

    def check_docs(self):
        if environ == "local":
            sys.stdout.write("\ncheck_docs - ignore")
        else:
            response = self.get("docs/")
            nose.assert_equal(response.status_code, 200)
            nose.assert_in("Brainiak API documentation!", response.text)
            sys.stdout.write("\ncheck_docs - pass")

    def check_instance_create(self):
        # Remove if instance exist
        self.put("place/City/globoland", "new_city.json")
        self.delete("place/City/globoland")

        # SOLR read URL
        solr_host = solr_endpoint[self.environ]
        solr_relative_url = 'solr/select/?q=uri%3A%22http%3A%2F%2Fsemantica.globo.com%2Fplace%2FCity%2Fgloboland%22'
        solr_url = "{0}{1}".format(solr_host, solr_relative_url)

        # ElasticSearch read URL
        es_relative_url = 'semantica.place/_search?q=_resource_id:globoland'
        es_host = elastic_search_endpoint[self.environ]
        es_url = "{0}{1}".format(es_host, es_relative_url)

        time.sleep(3)
        # Check if record does not exist in Solr
        solr_response = requests.get(solr_url)
        nose.assert_equal(solr_response.status_code, 200)
        nose.assert_in('numFound="0"', solr_response.text)

        # Check if instance does not exist in ElasticSearch
        es_response = requests.get(es_url)
        nose.assert_in(es_response.status_code, [200, 404])
        if es_response.status_code == 200:
            nose.assert_in('"total":0', es_response.text)

        # Add instance
        response = self.put("place/City/globoland", "new_city.json")
        nose.assert_equal(response.status_code, 201)

        sys.stdout.write("\n-- try changing <check_instance_create> timeout if it fails")
        time.sleep(3)

        # Check if instance was written in Virtuoso
        response_after = self.get("place/City/globoland")
        nose.assert_equal(response_after.status_code, 200)
        nose.assert_in('"upper:fullName": "Globoland (RJ)"', response_after.text)

        # Check if instance was written in Solr
        solr_response = requests.get(solr_url)
        nose.assert_equal(solr_response.status_code, 200)
        nose.assert_in('numFound="1"', solr_response.text)
        nose.assert_in('<str name="label">Globoland</str>', solr_response.text)

        # Check if instance was written in ElasticSearch
        es_response = requests.get(es_url)
        nose.assert_equal(response_after.status_code, 200)
        nose.assert_in('"total":1', es_response.text)

        sys.stdout.write("\ncheck_instance_create - pass")

    def check_instance_delete(self):
        self.put("place/City/globoland", "new_city.json")
        response = self.delete("place/City/globoland")
        nose.assert_equal(response.status_code, 204)
        response_after = self.get("place/City/globoland")
        nose.assert_equal(response_after.status_code, 404)
        sys.stdout.write("\ncheck_instance_delete - pass")


class MercuryChecker(Checker):

    def __init__(self, environ):
        Checker.__init__(self, environ)
        self.endpoint = mercury_endpoint.get(environ)

    def check_healthcheck(self):
        response = self.get("healthcheck/")
        nose.assert_equal(response.status_code, 200)
        nose.assert_in(u'WORKING', response.text)
        sys.stdout.write("\ncheck_healthcheck - pass")

    def check_status(self):
        response = self.get("status/")
        nose.assert_equal(response.status_code, 200)
        expected_piece = "Mercury is connected to event bus? YES"
        nose.assert_in(expected_piece, response.text)
        sys.stdout.write("\ncheck_status - pass")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        environ = sys.argv[-1]
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
