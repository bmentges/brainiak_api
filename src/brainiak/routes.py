from tornado.web import URLSpec
from brainiak.handlers import *

ROUTES = [
    # INTERNAL resources for monitoring and meta-infromation inspection
    URLSpec(r'/healthcheck/?', HealthcheckHandler),
    URLSpec(r'/_prefixes/?', PrefixHandler),
    URLSpec(r'/_query/?', StoredQueryCollectionHandler),
    URLSpec(r'/_query/(?P<query_id>[\w\-]+)/?', StoredQueryCRUDHandler),
    URLSpec(r'/_query/(?P<query_id>[\w\-]+)/_result?', StoredQueryExecutionHandler),
    URLSpec(r'/_status/?$', StatusHandler),
    URLSpec(r'/_status/activemq/?', EventBusStatusHandler),
    URLSpec(r'/_status/cache/?', CacheStatusHandler),
    URLSpec(r'/_status/virtuoso/?', VirtuosoStatusHandler),
    URLSpec(r'/_version/?', VersionHandler),

    URLSpec(r'/_schema_list/?', RootJsonSchemaHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_search/_schema_list/?', SearchJsonSchemaHandler),
    URLSpec(r'/_suggest/_schema_list/?', SuggestJsonSchemaHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/_schema_list/?', ContextJsonSchemaHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema_list/?', CollectionJsonSchemaHandler),

    # TEXTUAL search
    URLSpec(r'/_suggest/?', SuggestHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_search/?', SearchHandler),
    # resources that represents CONCEPTS
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/_schema/?', ClassHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/?', CollectionHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/(?P<class_name>[\w\-]+)/(?P<instance_id>[\w\-]+)/?', InstanceHandler),
    URLSpec(r'/(?P<context_name>[\w\-]+)/?', ContextHandler),
    URLSpec(r'/$', RootHandler),
    URLSpec(r'/.*$', UnmatchedHandler),
]
