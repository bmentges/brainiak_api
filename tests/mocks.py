# -*- coding: utf-8 -*-
from urlparse import urlparse, parse_qs
from brainiak.prefixes import expand_uri
from brainiak.utils.params import normalize_last_slash


triplestore_config = {
    'url': 'http://localhost:8890/sparql-auth',
    'app_name': 'Brainiak',
    'auth_mode': 'digest',
    'auth_username': 'api-semantica',
    'auth_password': 'api-semantica'
}


def mock_schema(properties_and_types_dict, id, context=None):
    properties_schema = {}
    type2datatype = {'string': 'xsd:string',
                     'integer': 'xsd:integer',
                     'date': 'xsd:date',
                     'datetime': 'xsd:dateTime',
                     'boolean': 'xsd:boolean'}
    for property_name, type_value in properties_and_types_dict.items():
        property_uri = expand_uri(property_name, context=context)
        if type_value is None:
            properties_schema[property_uri] = {'range': {'type': 'string', 'format': 'uri'}}
        else:
            properties_schema[property_uri] = {'type': type_value, 'datatype': expand_uri(type2datatype[type_value], context=context)}
    schema = {'properties': properties_schema}

    if id is not None:
        schema["id"] = id

    return schema


class MockSimpleRequest(object):

    def __init__(self, status_code, json):
        self.status_code = status_code
        self._json = json

    def __call__(self, *args, **kw):
        return self

    def json(self):
        return self._json

    @property
    def text(self):
        return self._json


class MockRequest(object):

    def __init__(self,
                 uri="http://localhost:5100/ctx/klass/",
                 query_string="",
                 instance=""):
        self.query = query_string
        self.uri = uri
        if instance:
            self.uri = u"%s%s" % (self.uri, instance)
        parsed_url = urlparse(self.uri)
        self.path = parsed_url.path
        self.protocol = parsed_url.scheme
        self.host = parsed_url.netloc
        self.base_url = u"{0}://{1}{2}".format(self.protocol, self.host, normalize_last_slash(self.path))
        self.resource_url = self.base_url + "{resource_id}"
        self.headers = {'Host': self.host}
        if query_string:
            self.uri = u"%s?%s" % (self.uri, query_string)

    def full_url(self):
        return self.uri


class MockResponse(object):

    def __init__(self, body):
        self.body = body


class MockHandler():

    def __init__(self, uri=None, querystring="", headers=None, **kw):
        self.kw = kw
        if uri is None:
            uri = 'http://mock.test.com/'
        self._querystring = querystring
        if headers is None:
            self._headers = {}
        else:
            self._headers = headers
        _parsed_url = urlparse(uri)
        self._path = _parsed_url.path
        self._protocol = _parsed_url.scheme
        self._host = _parsed_url.netloc
        self._uri = uri
        if not querystring in uri:
            self._uri = "{0}?{1}".format(uri, querystring)

        query_dict = parse_qs(querystring, keep_blank_values=True)
        for key, value in query_dict.items():
            first_value = value[0]
            if isinstance(first_value, str):
                unicode_value = first_value.decode('utf-8')
            elif isinstance(first_value, unicode):
                unicode_value = first_value
            else:
                raise Exception('Unexpected value {0} of type {1}'.format(first_value, type(first_value)))
            kw[key] = unicode_value

    def get_argument(self, key):
        return self.kw.get(key)

    @property
    def request(self):
        class Dummy(object):
            @property
            def arguments(inner_self):
                return self.kw.keys()

            @property
            def protocol(inner_self):
                return self._protocol

            @property
            def host(inner_self):
                return self._host

            @property
            def path(inner_self):
                return self._path

            @property
            def query(inner_self):
                return self._querystring

            @property
            def uri(inner_self):
                return self._uri

            @property
            def headers(inner_self):
                return self._headers

        d = Dummy()
        return d


class Params(dict):

    def __init__(self, params):
        self.triplestore_config = triplestore_config
        self.update(params)
