import logging


DEBUG = True
ENVIRONMENT = 'local'

SERVER_PORT = 5100

SPARQL_ENDPOINT = 'http://localhost:8890/sparql-auth'
SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"

DEFAULT_LANG = "pt"

LOG_FILEPATH = "/tmp/brainiak.log"
LOG_LEVEL = logging.DEBUG
LOG_NAME = "brainiak"

URI_PREFIX = "http://semantica.globo.com/"

DEFAULT_PER_PAGE = "10"
DEFAULT_PAGE = "0"

EVENT_BUS_HOST = "localhost"
EVENT_BUS_PORT = 61613

CORS_HEADERS = 'Content-Type, Authorization'
