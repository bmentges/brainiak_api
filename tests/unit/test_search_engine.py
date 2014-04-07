# coding:utf8

import logging
import time
from unittest import TestCase

from mock import patch, Mock

from tornado.web import HTTPError

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

    @patch("brainiak.search_engine._get_response",
           return_value=MockResponse('{}', 200))
    def test_run_analyze(self, request_mock):
        response = search_engine.run_analyze(
            target="sometext",
            analyzer="default",
            indexes="index1")
        self.assertEquals(response, {})

        call_args = request_mock.call_args[0][0]
        self.assertEqual(call_args["url"], u'http://localhost:9200/index1/_analyze?text=sometext')
        self.assertEqual(call_args["method"], u'GET')
        self.assertEqual(call_args["headers"], {u'Content-Type': u'application/x-www-form-urlencoded'})

    @patch("brainiak.search_engine.log.logger.info")
    @patch("brainiak.search_engine.log.logger",
           logging.getLogger("test"))
    @patch("brainiak.search_engine._do_request",
           return_value=MockResponse("{}", 200))
    def test_run_search(self, request_mock, info_mock):

        response = search_engine.run_search(
            body={},
            indexes=["index1"]
        )
        self.assertEquals(response, {})

        call_args = request_mock.call_args[0][0]
        self.assertEqual(call_args["url"], u'http://localhost:9200/index1/_search')
        self.assertEqual(call_args["method"], u'POST')
        self.assertEqual(call_args["headers"], {u'Content-Type': u'application/x-www-form-urlencoded'})
        self.assertEqual(call_args["body"], u"{}")

    @patch("brainiak.search_engine.log.logger.info")
    @patch("brainiak.search_engine._do_request",
           return_value=MockResponse("{}", 200))
    def test_save_instance_return_200(self, request_mock, mock_log_info):
        response = search_engine.save_instance({"test": "a"}, "index", "type", "id")
        expected_url = u"http://localhost:9200/index/type/id"
        expected_method = "PUT"
        expected_body = u'{"test": "a"}'
        call_args = request_mock.call_args[0][0]
        self.assertEqual(call_args["url"], expected_url)
        self.assertEqual(call_args["method"], expected_method)
        self.assertEqual(call_args["body"], expected_body)

        expected_returned_code = 200
        self.assertEquals(response, expected_returned_code)

    @patch("brainiak.search_engine._get_response",
           return_value=MockResponse('{"error"}', 400))
    def test_save_instance_return_400(self, request_mock):
        expected_msg = 'Error on Elastic Search when saving an instance.\n  PUT http://localhost:9200/index/type/id - 400\n  Body: {"error"}'
        try:
            search_engine.save_instance({"error": "json not in conformance with mapping, ES returns 400"}, "index", "type", "id")
        except HTTPError as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(e.log_message, expected_msg)

    @patch("brainiak.search_engine.log.logger.info")
    @patch("brainiak.search_engine._get_response",
           return_value=MockResponse('{"my_instance": 123}', 200))
    def test_get_instance_return_200(self, request_mock, mock_log_info):
        instance = search_engine.get_instance("index", "type", "id")
        self.assertEqual(instance, {"my_instance": 123})

    @patch("brainiak.search_engine._get_response",
           side_effect=HTTPError(500, log_message="xubi"))
    def test_get_instance_return_500(self, request_mock):
        expected_msg = 'xubi'
        try:
            search_engine.get_instance("index", "type", "id")
        except HTTPError as e:
            self.assertEqual(e.status_code, 500)
            self.assertEqual(e.log_message, expected_msg)

    @patch("brainiak.search_engine._do_request",
          return_value=MockResponse("{}", 200))
    def test_get_response(self, mock_do_request):
        expected_code = 200
        response = search_engine._get_response({})
        self.assertEqual(response.code, expected_code)

    @patch("brainiak.search_engine._do_request",
           side_effect=HTTPError(400, log_message="error"))
    def test_get_response_raises_httperror(self, mock_do_request):
        expected_code = 400
        expected_msg = "error"
        try:
            search_engine._get_response({})
        except HTTPError as e:
            self.assertEqual(e.status_code, expected_code)
            self.assertEqual(e.log_message, expected_msg)

    @patch("brainiak.log.logger.info")
    @patch("brainiak.search_engine.greenlet_fetch",
           return_value=MockResponse("{}", 200))
    def test_do_request(self, fetch_mock, mock_log_info):
        expected_msg = u'ELASTICSEARCH - GET - http://a-url.com - 200 - [time: 0] - BODY - {}'
        expected_code = 200
        # mock time.time
        time_patcher = patch.object(
            search_engine, 'time',
            Mock(wraps=time)
        )
        mocked_time = time_patcher.start()
        mocked_time.time.return_value = 0
        self.addCleanup(time_patcher.stop)
        # end mock time.time

        request_params = {
            "url": "http://a-url.com",
            "method": "GET",
        }
        response = search_engine._do_request(request_params)
        self.assertEquals(response.code, expected_code)
        mock_log_info.assert_called_with(expected_msg)
