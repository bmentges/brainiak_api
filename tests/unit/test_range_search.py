from unittest import TestCase

from brainiak.range_search.range_search import _build_body_query


class RangeSearchTestCase(TestCase):

    def test_build_query_body(self):
        expected = {
            "query": {
                "query_string": {
                    "query": "rio AND de AND jan*"
                }
            }
        }

        params = {
            "pattern": "Rio De Jan"
        }

        response = _build_body_query(params)
        self.assertEqual(expected, response)
