from unittest import TestCase

from brainiak.handlers import ClassHandler, VersionHandler, \
    HealthcheckHandler, VirtuosoStatusHandler, InstanceHandler, SuggestHandler, \
    StoredQueryCollectionHandler, StoredQueryCRUDHandler, StoredQueryCRUDHandler, \
    StoredQueryExecutionHandler
from brainiak.routes import ROUTES


class RouteTestCase(TestCase):

    def test_healthcheck(self):
        regex = self._regex_for(HealthcheckHandler)
        HEALTCHECK_SUFFIX = '/healthcheck'
        self.assertTrue(regex.match(HEALTCHECK_SUFFIX))

    def test_version(self):
        regex = self._regex_for(VersionHandler)
        VERSION_SUFFIX = '/_version'
        self.assertTrue(regex.match(VERSION_SUFFIX))

    def test_status_virtuoso(self):
        regex = self._regex_for(VirtuosoStatusHandler)
        VIRTUOSO_STATUS = '/_status/virtuoso'
        self.assertTrue(regex.match(VIRTUOSO_STATUS))

    def test_range_search(self):
        regex = self._regex_for(SuggestHandler)
        VIRTUOSO_STATUS = '/_suggest'
        self.assertTrue(regex.match(VIRTUOSO_STATUS))

    def test_schema_resource(self):
        regex = self._regex_for(ClassHandler)
        VALID_SCHEMA_RESOURCE_SUFFIX = '/person/Gender/_schema'
        match_pattern = regex.match(VALID_SCHEMA_RESOURCE_SUFFIX)

        expected_params = {"context_name": "person", "class_name": "Gender"}
        self.assertTrue(self._groups_match(match_pattern, expected_params))

    def test_invalid_schema_resource(self):
        regex = self._regex_for(ClassHandler)
        INVALID_SCHEMA_RESOURCE_SUFFIX = '/person/Gender/'
        match_pattern = regex.match(INVALID_SCHEMA_RESOURCE_SUFFIX)

        self.assertFalse(self._groups_match(match_pattern, {}))

    def test_invalid_schema_resource_with_unexpected_params(self):
        regex = self._regex_for(ClassHandler)
        VALID_SCHEMA_RESOURCE_SUFFIX = '/person/Gender/_schema'
        match_pattern = regex.match(VALID_SCHEMA_RESOURCE_SUFFIX)

        unexpected_params = {"context_name": "person",
                             "class_name": "Gender",
                             "unexpected_param": "param"}
        self.assertFalse(self._groups_match(match_pattern, unexpected_params))

    def test_invalid_schema_resource_nonexistent_suffix(self):
        regex = self._regex_for(ClassHandler)
        INVALID_SCHEMA_RESOURCE_SUFFIX = '/person/Gender/_class_schema'
        match_pattern = regex.match(INVALID_SCHEMA_RESOURCE_SUFFIX)

        unexpected_params = {"context_name": "person", "class_name": "Gender"}
        self.assertFalse(self._groups_match(match_pattern, unexpected_params))

    def test_instance_resource(self):
        regex = self._regex_for(InstanceHandler)
        VALID_INSTANCE_RESOURCE_SUFFIX = "/person/Gender/Male"
        match_pattern = regex.match(VALID_INSTANCE_RESOURCE_SUFFIX)

        expected_params = {"context_name": "person",
                           "class_name": "Gender",
                           "instance_id": "Male"}
        self.assertTrue(self._groups_match(match_pattern, expected_params))

    def test_instance_resource_nonexistent_params(self):
        regex = self._regex_for(InstanceHandler)
        VALID_INSTANCE_RESOURCE_SUFFIX = "/person/Gender/Male"
        match_pattern = regex.match(VALID_INSTANCE_RESOURCE_SUFFIX)

        expected_params = {"context_name": "person",
                           "class_name": "Gender",
                           "crazy_parameter": "crazy_value"}
        self.assertFalse(self._groups_match(match_pattern, expected_params))

    def test_stored_query_route_list_all(self):
        regex = self._regex_for(StoredQueryCollectionHandler)
        VALID_STORED_QUERY_COLLECTION_SUFFIX = "/_query"
        match = regex.match(VALID_STORED_QUERY_COLLECTION_SUFFIX)
        self.assertTrue(match is not None)

    def test_stored_query_route_crud(self):
        regex = self._regex_for(StoredQueryCRUDHandler)
        VALID_STORED_QUERY_CRUD_SUFFIX = "/_query/query_id"
        match_pattern = regex.match(VALID_STORED_QUERY_CRUD_SUFFIX)

        expected_params = {"query_id": "query_id"}
        self.assertTrue(self._groups_match(match_pattern, expected_params))

    def test_stored_query_route_execution(self):
        regex = self._regex_for(StoredQueryExecutionHandler)
        VALID_INSTANCE_RESOURCE_SUFFIX = "/_query/query_id/_result"
        match_pattern = regex.match(VALID_INSTANCE_RESOURCE_SUFFIX)

        expected_params = {"query_id": "query_id"}
        self.assertTrue(self._groups_match(match_pattern, expected_params))

    def _regex_for(self, klass):
        return filter(lambda u: u.handler_class == klass, ROUTES)[0].regex

    def _groups_match(self, match, groups):
        if match is None or len(groups) == 0:
            return False

        for group in groups.keys():
            try:
                if not match.group(group) == groups[group]:
                    return False
            except IndexError:
                return False

        return True
