import os
import re
import shutil
import subprocess
import unittest
import urllib2

import rdflib

from brainiak import settings, triplestore
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
ISQL_DROP = "SPARQL DROP GRAPH <%(graph)s>;"

ISQL_SERVER = "select server_root();"
ISQL_INFERENCE = "rdfs_rule_set('%(graph_uri)sruleset', '%(graph_uri)s');"
ISQL_REMOVE_INFERENCE = "rdfs_rule_set('%(graph_uri)sruleset', '%(graph_uri)s', 1);"


def mocked_convert(self):
    return self.response


def run_isql(cmd):
    if hasattr(settings, "REMOTE_ISQL"):
        isql = settings.REMOTE_ISQL
    else:
        isql = ISQL

    isql_cmd = ISQL_CMD % (cmd, isql)
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
    return run_isql(cmd)


def disable_inference_at_graph(graph_uri):
    cmd = ISQL_REMOVE_INFERENCE % {"graph_uri": graph_uri}
    return run_isql(cmd)


class QueryTestCase(SimpleTestCase):
    """
    Used for testing SPARQL queries.

    Provides two approaches:

    - directly read / write from a SPARQL Endpoint
    - emulate a SPARQL Endpoint using RDFlib in-memory graph (faster)
    """

    allow_inference = True
    fixtures = []
    fixtures_by_graph = {}

    @property
    def graph_uri(self):
        return GRAPH_URI

    @graph_uri.setter
    def graph_uri(self, value):
        global GRAPH_URI
        GRAPH_URI = value

    def _load_fixture_to_memory(self, fixture, graph=None):
        graph.parse(fixture, format="n3")

    def _load_fixture_to_triplestore(self, fixture, graph):
        fixture = copy_ttl_to_virtuoso_dir(fixture)
        isql_up = ISQL_UP % {"ttl": fixture, "graph": graph}
        run_isql(isql_up)

    def _pre_setup(self):
        self.remove_inference_options()

        self._drop_graph_from_triplestore(self.graph_uri)

        load = self._load_fixture_to_triplestore

        if not self.fixtures_by_graph:
            for fixture in self.fixtures:
                load(fixture, self.graph_uri)
        else:
            for (graph, fixtures) in self.fixtures_by_graph.items():
                for fixture in fixtures:
                    load(fixture, graph)

        self.process_inference_options()

    def _drop_graph_from_triplestore(self, graph):
        isql_down = ISQL_DOWN % {"graph": graph}
        run_isql(isql_down)
        try:
            isql_drop = ISQL_DROP % {"graph": graph}
            run_isql(isql_drop)
        except Exception, e:
            pass
            #print(e)

    def _post_teardown(self):
        self.remove_inference_options()
        if not self.fixtures_by_graph:
            self._drop_graph_from_triplestore(self.graph_uri)
        else:
            for graph in self.fixtures_by_graph.keys():
                self._drop_graph_from_triplestore(graph)

    def process_inference_options(self):
        #if self.allow_inference:
        if not self.fixtures_by_graph:
            enable_inference_at_graph(self.graph_uri)
        else:
            for graph_ in self.fixtures_by_graph.keys():
                enable_inference_at_graph(graph_)

    def remove_inference_options(self):
        #if self.allow_inference:
        if not self.fixtures_by_graph:
            disable_inference_at_graph(self.graph_uri)
        else:
            for graph_ in self.fixtures_by_graph.keys():
                disable_inference_at_graph(graph_)

    def query(self, query_string, graph=None):
        endpoint_dict = parse_section()
        self.process_inference_options()
        response = triplestore.query_sparql(query_string, endpoint_dict, async=False)
        return response
