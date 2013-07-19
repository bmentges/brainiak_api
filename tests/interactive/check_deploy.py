import inspect
import json
import sys
import unittest

import nose.tools as nose
import requests

version = "2.0.0"

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

	# def check_activemq(self):
	# 	response = self.get("_status/activemq")
	# 	nose.assert_equal(response.status_code, 200)
	# 	nose.assert_in("SUCCEED", response.text)
	# 	sys.stdout.write("\ncheck_activemq - pass")

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

	# def check_version(self):
	# 	response = self.get("_version")
	# 	nose.assert_equal(response.status_code, 200)
	# 	nose.assert_in(version, response.text)
	# 	sys.stdout.write("\ncheck_version - pass")

	def check_docs(self):
		if environ == "local":
			sys.stdout.write("\ncheck_docs - ignore")
		else:
			response = self.get("docs/")
			nose.assert_equal(response.status_code, 200)
			nose.assert_in("Brainiak API documentation!", response.text)
			sys.stdout.write("\ncheck_docs - pass")

	def check_instance_create(self):
		self.delete("place/City/globoland")
		response = self.put("place/City/globoland", "new_city.json")
		nose.assert_equal(response.status_code, 201)
		sys.stdout.write("\ncheck_instance_create - pass")

	def check_instance_delete(self):
		self.put("place/City/globoland", "new_city.json")
		response = self.delete("place/City/globoland")
		nose.assert_equal(response.status_code, 204)
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
