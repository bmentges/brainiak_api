# coding:utf8

import logging
import time
from unittest import TestCase

from mock import patch, Mock
from tornado.httpclient import HTTPResponse, HTTPRequest

from brainiak import search_engine
from tests.mocks import MockResponse


class SearchEngineTestCase(TestCase):

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_request_url_all_none(self):
        expected_url = "http://esearch.host/semantica.*/_search"
        response = search_engine._build_elasticsearch_request_url(None)
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_request_url(self):
        expected_url = "http://esearch.host/semantica.glb/_search"
        response = search_engine._build_elasticsearch_request_url(["semantica.glb"])
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_default_usage(self):
        expected_url = "http://esearch.host/index1/_analyze?text=something"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1"],
            analyzer="default",
            target="something")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_special_characters(self):
        expected_url = "http://esearch.host/index1/_analyze?text=%C5%9A%E1%B9%95%C3%A9c%C3%AC%C3%A3l+ch%C3%A2rs"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1"],
            analyzer="default",
            target="Śṕécìãl chârs")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_special_characters_encoded(self):
        expected_url = "http://esearch.host/index1/_analyze?text=galv%C3%A3o"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1"],
            analyzer="default",
            target=u"galv\xe3o")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_with_multiple_indexes(self):
        expected_url = "http://esearch.host/index1,index2/_analyze?text=anything"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1", "index2"],
            analyzer="default",
            target="anything")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_with_non_default_analyzer(self):
        expected_url = "http://esearch.host/index1/_analyze?analyzer=special_analyzer&text=dummything"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1"],
            analyzer="special_analyzer",
            target="dummything")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.ELASTICSEARCH_ENDPOINT", "esearch.host")
    def test_build_elasticsearch_analyze_url_with_text_that_needs_scaping(self):
        expected_url = "http://esearch.host/index1/_analyze?text=text+with+spaces"
        response = search_engine._build_elasticsearch_analyze_url(
            indexes=["index1"],
            analyzer="default",
            target="text with spaces")
        self.assertEquals(expected_url, response)

    @patch("brainiak.search_engine.greenlet_fetch", return_value=MockResponse("{}"))
    def test_run_analyze(self, greenlet_fetch_mock):
        response = search_engine.run_analyze(
            target="sometext",
            analyzer="default",
            indexes="index1")
        self.assertEquals(response, {})

        call_args = greenlet_fetch_mock.call_args[0][0]
        self.assertEqual(call_args.url, u'http://localhost:9200/index1/_analyze?text=sometext')
        self.assertEqual(call_args.method, u'GET')
        self.assertEqual(call_args.headers, {u'Content-Type': u'application/x-www-form-urlencoded'})

    @patch("brainiak.search_engine.log.logger.info")
    @patch("brainiak.search_engine.log.logger", logging.getLogger("test"))
    @patch("brainiak.search_engine.greenlet_fetch", return_value=MockResponse("{}"))
    def test_run_search(self, greenlet_fetch_mock, info_mock):
        # mock time.time
        time_patcher = patch.object(
            search_engine, 'time',
            Mock(wraps=time)
        )
        mocked_time = time_patcher.start()
        mocked_time.time.return_value = 0
        self.addCleanup(time_patcher.stop)
        # end mock time.time

        response = search_engine.run_search(
            body={},
            indexes=["index1"]
        )
        self.assertEquals(response, {})

        call_args = greenlet_fetch_mock.call_args[0][0]
        self.assertEqual(call_args.url, u'http://localhost:9200/index1/_search')
        self.assertEqual(call_args.method, u'POST')
        self.assertEqual(call_args.headers, {u'Content-Type': u'application/x-www-form-urlencoded'})
        self.assertEqual(call_args.body, u"{}")

        msgs = info_mock.call_args
        msg1 = msgs[0][0]
        msg2 = msgs[1]

        expected_msg1 = u'ELASTICSEARCH - http://localhost:9200/index1/_search - POST [time: 0] - QUERY - {}'
        expected_msg2 = {}
        self.assertEqual(msg1, expected_msg1)
        self.assertEqual(msg2, expected_msg2)
