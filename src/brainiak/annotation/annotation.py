from tornado.httpclient import HTTPError

from ..greenlet_tornado import greenlet_asynchronous
from ..handlers import BrainiakRequestHandler, schema_resource
from ..prefixes import normalize_all_uris_recursively, SHORTEN


class AnnotationHandler(BrainiakRequestHandler):
    SUPPORTED_METHODS = list("GET")

    @greenlet_asynchronous
    def get(self, context_name, class_name):
        # self.request.query = unquote(self.request.query)
        #
        # with safe_params():
        #     self.query_params = ParamDict(self,
        #                                   context_name=context_name,
        #                                   class_name=class_name)
        # del context_name
        # del class_name
        #
        try:
            response = schema_resource.get_cached_schema(self.query_params, include_meta=True)
        except schema_resource.SchemaNotFound, e:
            raise HTTPError(404, log_message=e.message)

        if self.query_params['expand_uri'] == "0":
            response = normalize_all_uris_recursively(response, mode=SHORTEN)
        self.add_cache_headers(response['meta'])
        self.finalize(response['body'])
