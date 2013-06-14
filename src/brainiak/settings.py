import logging


DEBUG = True
ENVIRONMENT = 'local'

SPARQL_PORT = 8890
SPARQL_ENDPOINT = 'http://localhost:%d/sparql-auth' % SPARQL_PORT
SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"

DEFAULT_LANG = "pt"

DEFAULT_PER_PAGE = "10"
DEFAULT_PAGE = "0"

LOG_FILEPATH = "/tmp/brainiak.log"
LOG_LEVEL = logging.DEBUG
LOG_NAME = "brainiak"

URI_PREFIX = "http://semantica.globo.com/"

EVENT_BUS_HOST = "localhost"
EVENT_BUS_PORT = 61613
NOTIFY_BUS = True

DEFAULT_RULESET_URI = "http://semantica.globo.com/ruleset"

CORS_HEADERS = 'Content-Type, Authorization'

SERVER_PORT = 5100

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
ENABLE_CACHE = False  # Locally, keep this == False, so tests won't be affected
