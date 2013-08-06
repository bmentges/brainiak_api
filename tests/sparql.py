import os
import re
import shutil
import subprocess
import unittest

import rdflib
from SPARQLWrapper import Wrapper, JSON

from brainiak.utils.config_parser import parse_section


def strip(query_string):
    return [item.strip() for item in query_string.split("\n") if item.strip() != '']


class SimpleTestCase(unittest.TestCase):

    maxDiff = None

    def __call__(self, *args, **kwds):
        """
        Wrapper around default __call__ method to perform common test
        set up. This means that user-defined Test Cases aren't required to
        include a call to super().setUp().
        """
        #result = kwds.get("result", None)

        try:
            self._pre_setup()
        except (KeyboardInterrupt, SystemExit):
            raise
        #except Exception:
        #    result.addError(self, sys.exc_info())
        #    return

        super(SimpleTestCase, self).__call__(*args, **kwds)

        try:
            self._post_teardown()
        except (KeyboardInterrupt, SystemExit):
            raise
        #except Exception:
        #    result.addError(self, sys.exc_info())
        #    return

    def _pre_setup(self):
        "Hook method for setting up the test fixture before default setUp."
        pass

    def _post_teardown(self):
        "Hook method for setting up the test fixture after default tearDown."
        pass


GRAPH_URI = "http://test.graph/"
graph = rdflib.Graph()

ISQL = "isql"
ISQL_CMD = 'echo "%s" | %s'
ISQL_UP = "DB.DBA.TTLP_MT_LOCAL_FILE('%(ttl)s', '', '%(graph)s');"
ISQL_DOWN = "SPARQL CLEAR GRAPH <%(graph)s>;"
ISQL_SERVER = "select server_root();"
ISQL_INFERENCE = "rdfs_rule_set('%(graph_uri)sruleset', '%(graph_uri)s');"


def mocked_query(self):

    qres = graph.query(self.queryString)

    bindings_list = []
    for row in qres.bindings:
        row_dict = {}
        for key, value in row.items():
            if not value:
                continue

            row_item = {}

            if isinstance(value, rdflib.term.URIRef):
                type_ = 'uri'
            elif isinstance(value, rdflib.term.Literal):
                if hasattr(value, 'datatype') and value.datatype:
                    type_ = 'typed-literal'
                    row_item["datatype"] = value.datatype
                else:
                    type_ = 'literal'
            else:
                raise Exception('Unkown type')

            row_item["type"] = type_
            row_item["value"] = str(value)

            row_dict[str(key)] = row_item

        bindings_list.append(row_dict)

    binding_str = {
        'results': {
            'bindings': bindings_list
        }
    }
    return Wrapper.QueryResult(binding_str)


def mocked_virtuoso_query(self):
    query = self.queryString
    graph = GRAPH_URI
    if query.find('INSERT') > -1:
        query = re.sub('GRAPH [^\s]+', 'GRAPH <%s>' % graph, query)
    elif query.find('FROM') == -1 and query.find('WHERE') > -1:
        splited_query = query.split('WHERE')
        splited_query.insert(1, 'FROM <%s> WHERE' % graph)
        return ' '.join(splited_query)
    else:
        query = re.sub('FROM [^\s]+', 'FROM <%s>' % graph, query)
    self.queryString = query
    return Wrapper.QueryResult(self._query())


def mocked_convert(self):
    return self.response


def run_isql(cmd):
    isql_cmd = ISQL_CMD % (cmd, ISQL)
    process = subprocess.Popen(isql_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = process.communicate()
    if stderr_value:
        raise Exception(stderr_value)
    return stdout_value


def copy_ttl_to_virtuoso_dir(ttl):
    virtuoso_dir = run_isql(ISQL_SERVER).split('\n\n')[-2]
    fixture_dir, fixture_file = os.path.split(ttl)
    shutil.copyfile(ttl, os.path.join(virtuoso_dir, fixture_file))
    return fixture_file


def remove_ttl_from_virtuoso_dir(ttl):
    virtuoso_dir = run_isql(ISQL_SERVER).split('\n\n')[-2]
    ttl_path = os.path.join(virtuoso_dir, ttl)
    os.remove(ttl_path)


def enable_inference_at_graph(graph_uri):
    cmd = ISQL_INFERENCE % {"graph_uri": graph_uri}
    virtuoso_response = run_isql(cmd)


class QueryTestCase(SimpleTestCase):
    """
    Used for testing SPARQL queries.

    Provides two approaches:

    - directly read / write from a SPARQL Endpoint
    - emulate a SPARQL Endpoint using RDFlib in-memory graph (faster)
    """

    allow_triplestore_connection = False
    allow_inference = True
    fixtures = []
    fixtures_by_graph = {}

    # Mock related
    originalSPARQLWrapper = Wrapper.SPARQLWrapper
    originalQueryResult = Wrapper.QueryResult
    originalQueryResultConvert = Wrapper.QueryResult.convert

    @property
    def graph_uri(self):
        return GRAPH_URI

    @graph_uri.setter
    def graph_uri(self, value):
        global GRAPH_URI
        GRAPH_URI = value

    def _setup_mocked_triplestore(self):
        Wrapper.SPARQLWrapper.query = mocked_query
        Wrapper.QueryResult.convert = mocked_convert
        Wrapper.SPARQLWrapper.query = mocked_virtuoso_query

    def _setup_triplestore(self):
        self._restore_triplestore()

    def _load_fixture_to_memory(self, fixture, graph=None):
        graph.parse(fixture, format="n3")

    def _load_fixture_to_triplestore(self, fixture, graph):
        fixture = copy_ttl_to_virtuoso_dir(fixture)
        isql_up = ISQL_UP % {"ttl": fixture, "graph": graph}
        run_isql(isql_up)

    def _pre_setup(self):
        self._drop_graph_from_triplestore(self.graph_uri)
        if self.allow_triplestore_connection:
            setup = self._setup_triplestore
            load = self._load_fixture_to_triplestore
            self.process_inference_options()
        else:
            setup = self._setup_mocked_triplestore
            load = self._load_fixture_to_memory

        if not self.fixtures_by_graph:
            setup()
            for fixture in self.fixtures:
                load(fixture, self.graph_uri)
        else:
            setup()
            for (graph, fixtures) in self.fixtures_by_graph.items():
                for fixture in fixtures:
                    load(fixture, graph)

    def _drop_graph_from_triplestore(self, graph):
        isql_down = ISQL_DOWN % {"graph": graph}
        run_isql(isql_down)

    def _restore_triplestore(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult
        Wrapper.QueryResult.convert = self.originalQueryResultConvert

    def _post_teardown(self):
        self._restore_triplestore()
        if not self.fixtures_by_graph:
            if self.allow_triplestore_connection:
                self._drop_graph_from_triplestore(self.graph_uri)
        else:
            for graph in self.fixtures_by_graph.keys():
                self._drop_graph_from_triplestore(graph)

    def process_inference_options(self):
        if not self.fixtures_by_graph:
            if self.allow_inference:
                enable_inference_at_graph(self.graph_uri)
        else:
            for graph_ in self.fixtures_by_graph.keys():
                enable_inference_at_graph(graph_)

    def query(self, query_string, graph=None):
        endpoint_dict = parse_section()
        user = endpoint_dict["auth_username"]
        password = endpoint_dict["auth_password"]
        mode = endpoint_dict["auth_mode"]
        endpoint = endpoint_dict["url"]
        realm = "SPARQL"

        self.process_inference_options()

        endpoint = Wrapper.SPARQLWrapper(endpoint)
        endpoint.setCredentials(user, password, mode=mode, realm=realm)
        endpoint.setReturnFormat(JSON)
        endpoint.setQuery(query_string)

        response = endpoint.query().convert()
        return response
