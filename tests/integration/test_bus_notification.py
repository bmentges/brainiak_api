from mock import patch
import json
from brainiak import server
from brainiak.instance import create_resource, edit_resource
from brainiak.utils.sparql import is_modify_response_successful

from tests.tornado_cases import TornadoAsyncHTTPTestCase
from tests.sparql import QueryTestCase



class BusNotificationTestCase(TornadoAsyncHTTPTestCase, QueryTestCase):

    maxDiff = None
    # The class variables below are handled by QueryTestCase
    allow_triplestore_connection = True
    graph_uri = "http://somegraph.org/"
    fixtures = ["tests/sample/instances.n3"]

    def get_app(self):
        return server.Application()

    def setUp(self):
        super(BusNotificationTestCase, self).setUp()

    def tearDown(self):
        pass

    @patch("brainiak.handlers.log")
    def test_edit_instance_200_adding_predicate(self, log):
        modified_new_york = self.fetch('/anything/Place/new_york?class_prefix=http://tatipedia.org/&instance_prefix=http://tatipedia.org/&graph_uri=http://somegraph.org/',
                                       method='PUT',
                                       body=json.dumps({}))
        self.assertEqual(modified_new_york.code, 200)
        # TODO assert bus notification
